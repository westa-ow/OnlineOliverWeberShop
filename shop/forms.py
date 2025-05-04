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

        # If the checkbox is checked, the link field is mandatory
        if with_link and not link:
            self.add_error('link', 'Please enter a link if the option "With Link" is checked.')
        # If the checkbox is not checked, you can reset the value of the link field
        if not with_link:
            cleaned_data['link'] = ''
        return cleaned_data

    def save(self, commit=True):
        # First we save the base Banner object
        banner = super().save(commit=False)
        if commit:
            banner.save()
        else:
            # If commit=False, no relationship can be created later because the banner pk will not be set
            raise ValueError("commit=False is not supported in this form.")

        # After saving the object, clear (delete old) links and create new ones
        selected_languages = self.cleaned_data['languages']
        # If you are editing an existing banner, delete the links already created,
        # in order to create new ones according to the selected languages.
        BannerLanguage.objects.filter(banner=banner).delete()

        for language in selected_languages:
            # Find the maximum priority for this language and assign the following sequence number
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
        # If you are editing an existing banner, fill in the language selection
        self.fields['link'].required = False
        if self.instance and self.instance.pk:
            # Pass the list of id languages associated with the banner through the BannerLanguage intermediate model.
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

    gdpr_consent = forms.BooleanField(
        required=True,
        label=_("I consent to the processing and use of my personal data in accordance with GDPR"),
        error_messages={
            'required': _("You must agree to the processing of your personal data to register.")
        }
    )
    class Meta(UserCreationForm.Meta):
        model =User
        fields = ("social_title", "first_name", "last_name",  "email",  "birthdate", "offers", "receive_newsletter")