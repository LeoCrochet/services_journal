from django import forms
from django.contrib.auth.models import User

from .models import ROLE_ADMIN, ROLE_MANAGER, ROLE_OPERATOR, Branch, UserProfile


class BranchForm(forms.ModelForm):
    """Создание/редактирование площадки с данными подписанта."""

    class Meta:
        model = Branch
        fields = ["name", "code", "prefix", "signer_name", "signer_position"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "code": forms.TextInput(attrs={"class": "form-control"}),
            "prefix": forms.TextInput(attrs={"class": "form-control"}),
            "signer_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Например: Петров Петр Петрович"}
            ),
            "signer_position": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Например: Менеджер"}
            ),
        }


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
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "first_name": forms.TextInput(attrs={"placeholder": "Например: Иванов Иван", "class": "form-control"}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        password1 = forms.CharField(
            label="Пароль",
            required=self.instance.pk is None,
            widget=forms.PasswordInput(attrs={"autocomplete": "new-password", "class": "form-control"}),
            help_text="Минимум 8 символов.",
        )
        password2 = forms.CharField(
            label="Подтверждение пароля",
            required=self.instance.pk is None,
            widget=forms.PasswordInput(attrs={"autocomplete": "new-password", "class": "form-control"}),
        )
        self.fields["role"].widget.attrs["class"] = "form-select"
        self.fields["branch"].widget.attrs["class"] = "form-select"
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