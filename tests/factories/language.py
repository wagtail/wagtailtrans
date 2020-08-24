import factory

from wagtailtrans import models


class LanguageFactory(factory.django.DjangoModelFactory):
    code = 'en-gb'
    position = 0
    is_default = True
    live = True

    class Meta:
        model = models.Language
        django_get_or_create = ['code']
