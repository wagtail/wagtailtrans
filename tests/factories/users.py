import factory
from django.contrib.auth import get_user_model


class UserFactory(factory.django.DjangoModelFactory):

    first_name = 'John'
    last_name = 'Doe'
    email = factory.LazyAttribute(lambda a: '{0}.{1}@example.org'.format(a.first_name, a.last_name).lower())
    password = 'secret1234'

    class Meta:
        model = get_user_model()

    @classmethod
    def _create(cls, target_class, *args, **kwargs):
        password = kwargs.pop('password', None)
        user = super()._create(target_class, *args, **kwargs)

        if password:
            user.set_password(password)
            user.clear_password = password
            user.save()
        return user
