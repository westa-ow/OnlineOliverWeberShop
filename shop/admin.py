from django.contrib import admin
from .models import Banner, BannerLanguage, Language, Store


admin.site.register(Store)

class BannerLanguageInline(admin.TabularInline):
    model = BannerLanguage
    extra = 1  # Можно выставить нужное число «пустых» форм


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ('title', 'active')
    inlines = [BannerLanguageInline]
    # При необходимости можно добавить фильтр по языкам или настроить сортировку


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ('code', 'name')
