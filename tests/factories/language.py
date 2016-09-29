import factory

from wagtailtrans import models


class LanguageFactory(factory.DjangoModelFactory):
    order = 0
    code = 'en-gb'
    is_default = True
    live = True

    class Meta:
        model = models.Language
