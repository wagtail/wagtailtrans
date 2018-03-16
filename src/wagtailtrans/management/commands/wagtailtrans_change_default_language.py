from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand, CommandError

from wagtailtrans.models import Language
from wagtailtrans.utils.language_switch import change_default_language


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--language', type=str)

    def handle(self, language, *args, **kwargs):
        if not language:
            raise CommandError("Missing --language argument")
        try:
            new_default = Language.objects.get(code=language)
        except ObjectDoesNotExist:
            raise CommandError("Language is not yet set in your site")

        current_default = Language.objects.default()
        if new_default == current_default:
            raise CommandError("Language {} is already default language".format(new_default))

        change_default_language(new_default)
