from django.apps import AppConfig
from django.db.models.signals import post_migrate

ROLE_ADMIN = "admin"
ROLE_OPERATOR = "operator"


def create_role_groups(sender, **kwargs):
    from django.contrib.auth.models import Group

    Group.objects.get_or_create(name=ROLE_ADMIN)
    Group.objects.get_or_create(name=ROLE_OPERATOR)


class AccountsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.accounts"
    verbose_name = "Пользователи и роли"

    def ready(self):
        post_migrate.connect(create_role_groups, sender=self)