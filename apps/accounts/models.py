from django.contrib.auth.models import User
from django.db import models

ROLE_ADMIN = "admin"
ROLE_OPERATOR = "operator"
ROLE_MANAGER = "manager"

ROLE_CHOICES = [
    (ROLE_ADMIN, "Администратор"),
    (ROLE_OPERATOR, "Оператор"),
    (ROLE_MANAGER, "Руководитель"),
]


class Branch(models.Model):
    """Площадка/филиал компании."""

    name = models.CharField("Название", max_length=100)
    code = models.CharField("Код", max_length=10, unique=True)
    prefix = models.CharField("Префикс номера заявки", max_length=10, unique=True)
    signer_name = models.CharField("ФИО подписанта", max_length=150, blank=True)
    signer_position = models.CharField("Должность подписанта", max_length=120, blank=True)

    class Meta:
        verbose_name = "Площадка"
        verbose_name_plural = "Площадки"
        ordering = ["name"]

    def __str__(self):
        return self.name


class UserProfile(models.Model):
    """Дополнительные данные пользователя: роль и площадка."""

    user = models.OneToOneField(
        User,
        verbose_name="Пользователь",
        on_delete=models.CASCADE,
        related_name="profile",
    )
    role = models.CharField(
        "Роль",
        max_length=20,
        choices=ROLE_CHOICES,
        default=ROLE_OPERATOR,
    )
    branch = models.ForeignKey(
        Branch,
        verbose_name="Площадка",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="users",
        help_text="Обязательна для оператора. Для администратора/руководителя — пусто = доступ ко всем площадкам.",
    )

    class Meta:
        verbose_name = "Профиль пользователя"
        verbose_name_plural = "Профили пользователей"

    def __str__(self):
        return f"{self.user} — {self.get_role_display()}"