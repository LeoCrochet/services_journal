from django import forms

from apps.accounts.services import get_user_branch

from .models import Order, OrderItem


class OrderItemForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = ["service", "name", "description", "price"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"rows": 2, "class": "form-control"}),
            "price": forms.NumberInput(attrs={"step": "0.01", "class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["service"].widget.attrs.setdefault("class", "form-select")
        self.fields["service"].required = False


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ["branch", "number", "document_date", "client"]
        widgets = {
            "number": forms.TextInput(attrs={"placeholder": "Автоматически, если пусто", "class": "form-control"}),
            "document_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        for name, field in self.fields.items():
            if isinstance(field, forms.ModelChoiceField):
                field.widget.attrs.setdefault("class", "form-select")
            else:
                field.widget.attrs.setdefault("class", "form-control")

        # Оператор видит только свою площадку и не может её менять
        branch = get_user_branch(self.user) if self.user else None
        if branch is not None:
            self.fields["branch"].queryset = self.fields["branch"].queryset.filter(pk=branch.pk)
            self.fields["branch"].initial = branch

        self.fields["client"].queryset = self.fields["client"].queryset.select_related("branch")
        if branch is not None:
            self.fields["client"].queryset = self.fields["client"].queryset.filter(branch=branch)

    def clean(self):
        cleaned_data = super().clean()
        branch = cleaned_data.get("branch")
        client = cleaned_data.get("client")

        # Оператор не должен указывать заявку на другой филиал
        user_branch = get_user_branch(self.user) if self.user else None
        if user_branch is not None and branch is not None and branch.pk != user_branch.pk:
            self.add_error("branch", "Нельзя выбрать другую площадку.")

        if branch is not None and client is not None and client.branch_id != branch.pk:
            self.add_error("client", "Клиент принадлежит другой площадке.")

        return cleaned_data


OrderItemFormSet = forms.inlineformset_factory(
    Order,
    OrderItem,
    form=OrderItemForm,
    fields=["service", "name", "description", "price"],
    extra=1,
    can_delete=True,
)
