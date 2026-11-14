from django import forms

from apps.accounts.services import get_user_branch

from .models import Order, OrderItem


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ["branch", "number", "document_date", "client"]
        widgets = {
            "number": forms.TextInput(attrs={"placeholder": "Автоматически, если пусто"}),
            "document_date": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        # Оператор видит только свою площадку и не может её менять
        branch = get_user_branch(self.user) if self.user else None
        if branch is not None:
            self.fields["branch"].queryset = self.fields["branch"].queryset.filter(pk=branch.pk)
            self.fields["branch"].initial = branch

        self.fields["client"].queryset = self.fields["client"].queryset.select_related("branch")

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
    fields=["service", "name", "description", "price"],
    extra=1,
    can_delete=True,
)