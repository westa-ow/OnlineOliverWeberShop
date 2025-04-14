from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.db.models import Max
from django.utils.translation import gettext_lazy as _

from shop.models import Banner, Language, BannerLanguage

User = get_user_model()

class BannerForm(forms.ModelForm):
    languages = forms.ModelMultipleChoiceField(
        queryset=Language.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label="Languages"
    )
    class Meta:
        model = Banner
        # Поля формы: image, withLink, link и languages
        fields = ['image', 'withLink', 'link', 'languages']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['link'].required = False
    def clean(self):
        cleaned_data = super().clean()
        with_link = cleaned_data.get('withLink')
        link = cleaned_data.get('link')

        # Если галочка установлена, поле link обязательно для заполнения
        if with_link and not link:
            self.add_error('link', 'Please enter a link if the option "With Link" is checked.')
        # Если галочка не установлена, можно сбросить значение поля link
        if not with_link:
            cleaned_data['link'] = ''
        return cleaned_data

    def save(self, commit=True):
        # Сначала сохраняем базовый объект Banner
        banner = super().save(commit=False)
        if commit:
            banner.save()
        else:
            # Если commit=False, то позднее не получится создать отношения, т.к. pk баннера не будет задан
            raise ValueError("commit=False не поддерживается в этой форме.")

        # После сохранения объекта очищаем (удаляем старые) связи и создаём новые
        selected_languages = self.cleaned_data['languages']
        # Если редактируется уже существующий баннер, удаляем уже созданные связи,
        # чтобы затем создать новые согласно выбранным языкам.
        BannerLanguage.objects.filter(banner=banner).delete()

        for language in selected_languages:
            # Находим максимальный приоритет для данного языка и назначаем следующий порядковый номер
            max_priority = BannerLanguage.objects.filter(language=language).aggregate(Max('priority'))['priority__max'] or 0
            BannerLanguage.objects.create(
                banner=banner,
                language=language,
                priority=max_priority + 1
            )
        return banner


class EditBannerForm(forms.ModelForm):
    languages = forms.ModelMultipleChoiceField(
        queryset=Language.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label="Languages"
    )

    class Meta:
        model = Banner
        fields = ['withLink', 'link', 'languages']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Если редактируется существующий баннер, заполняем выбор языков
        self.fields['link'].required = False
        if self.instance and self.instance.pk:
            # Передаём список id языков, связанных с баннером через промежуточную модель BannerLanguage.
            self.fields['languages'].initial = self.instance.banner_languages.all().values_list('language__id', flat=True)


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(
        label = ("Email"),
        max_length = 254,
        widget = forms.EmailInput(attrs={'autocomplete' : 'email'})
    )
    first_name = forms.CharField(label="First Name", max_length=30, required=True)
    last_name = forms.CharField(label="Last Name", max_length=30, required=True)
    birthdate = forms.CharField(label="Birthdate", max_length=30, required=False)
    receive_newsletter = forms.BooleanField(label="Sign up for our newsletter", required=False)
    offers = forms.BooleanField(label="Receive offers from our partners", required=False)
    SOCIAL_TITLE_CHOICES = [
        (1, "Mr."),
        (2, "Mrs."),
    ]
    TYPE_OF_USER_CHOICES = [
        (1, "Customer"),
        (2, "B2B Customer"),
    ]
    social_title = forms.ChoiceField(
        choices=SOCIAL_TITLE_CHOICES,
        widget=forms.RadioSelect,
        label="Social title",
        required=False
    )
    class Meta(UserCreationForm.Meta):
        model =User
        fields = ("social_title", "first_name", "last_name",  "email",  "birthdate", "offers", "receive_newsletter")