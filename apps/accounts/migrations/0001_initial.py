import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


def create_default_branches(apps, schema_editor):
    Branch = apps.get_model("accounts", "Branch")
    Branch.objects.get_or_create(
        code="TLT",
        defaults={"name": "Тольятти", "prefix": "ТЛТ"},
    )
    Branch.objects.get_or_create(
        code="SZR",
        defaults={"name": "Сызрань", "prefix": "СЗР"},
    )


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Branch",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=100, verbose_name="Название")),
                ("code", models.CharField(max_length=10, unique=True, verbose_name="Код")),
                ("prefix", models.CharField(max_length=10, unique=True, verbose_name="Префикс номера заявки")),
            ],
            options={
                "verbose_name": "Площадка",
                "verbose_name_plural": "Площадки",
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="UserProfile",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "role",
                    models.CharField(
                        choices=[("admin", "Администратор"), ("operator", "Оператор"), ("manager", "Руководитель")],
                        default="operator",
                        max_length=20,
                        verbose_name="Роль",
                    ),
                ),
                (
                    "branch",
                    models.ForeignKey(
                        blank=True,
                        help_text="Обязательна для оператора. Для администратора/руководителя — пусто = доступ ко всем площадкам.",
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="users",
                        to="accounts.branch",
                        verbose_name="Площадка",
                    ),
                ),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="profile",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Пользователь",
                    ),
                ),
            ],
            options={
                "verbose_name": "Профиль пользователя",
                "verbose_name_plural": "Профили пользователей",
            },
        ),
        migrations.RunPython(create_default_branches, migrations.RunPython.noop),
    ]