from django.contrib import admin

from wagtail.wagtailtrans import models


class LanguageAdmin(admin.ModelAdmin):
    list_display = ('code', 'order', 'is_default')


class TranslatedPageAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'language')


admin.site.register(models.Language, LanguageAdmin)
admin.site.register(models.TranslatedPage, TranslatedPageAdmin)
