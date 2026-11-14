from django import forms
from django.contrib.auth.models import User

from .models import ROLE_ADMIN, ROLE_MANAGER, ROLE_OPERATOR, Branch, UserProfile


class UserForm(forms.ModelForm):
    """Создание/редактирование пользователя с ролью и площадкой."""

    role = forms.ChoiceField(
        label="Роль",
        choices=[(ROLE_ADMIN, "Администратор"), (ROLE_OPERATOR, "Оператор"), (ROLE_MANAGER, "Руководитель")],
    )
    branch = forms.ModelChoiceField(
        label="Площадка",
        queryset=Branch.objects.all(),
        required=False,
        help_text="Обязательна для оператора.",
    )

    class Meta:
        model = User
        fields = ["username", "first_name", "is_active"]
        labels = {
            "username": "Имя пользователя",
            "first_name": "ФИО",
            "is_active": "Активен",
        }
        widgets = {
            "first_name": forms.TextInput(attrs={"placeholder": "Например: Иванов Иван"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        password1 = forms.CharField(
            label="Пароль",
            required=self.instance.pk is None,
            widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
            help_text="Минимум 8 символов.",
        )
        password2 = forms.CharField(
            label="Подтверждение пароля",
            required=self.instance.pk is None,
            widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        )
        if self.instance.pk:
            password1.help_text = "Оставьте пустым, чтобы не менять."
        self.fields["password1"] = password1
        self.fields["password2"] = password2

        profile = getattr(self.instance, "profile", None)
        if profile is not None:
            self.fields["role"].initial = profile.role
            self.fields["branch"].initial = profile.branch

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")
        role = cleaned_data.get("role")
        branch = cleaned_data.get("branch")

        if password1 or password2:
            if password1 != password2:
                self.add_error("password2", "Пароли не совпадают.")
            elif password1 and len(password1) < 8:
                self.add_error("password1", "Пароль должен содержать минимум 8 символов.")

        if role == ROLE_OPERATOR and branch is None:
            self.add_error("branch", "Для оператора необходимо указать площадку.")

        if role in (ROLE_ADMIN, ROLE_MANAGER):
            cleaned_data["branch"] = None

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get("password1")

        if commit:
            if password:
                user.set_password(password)
            user.save()

        role = self.cleaned_data.get("role")
        branch = self.cleaned_data.get("branch")
        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.role = role
        profile.branch = branch
        profile.save()

        return user