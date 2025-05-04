from django.contrib import admin
from .models import Banner, BannerLanguage, Language, Store


admin.site.register(Store)

class BannerLanguageInline(admin.TabularInline):
    model = BannerLanguage
    extra = 1  # You can set the number of “empty” forms as desired


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ('title', 'active')
    inlines = [BannerLanguageInline]
    # If necessary, you can add a filter by language or customize sorting


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ('code', 'name')
