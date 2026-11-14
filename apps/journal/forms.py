from django import forms

from .models import Order, OrderItem


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ["number", "document_date", "client"]
        widgets = {
            "document_date": forms.DateInput(attrs={"type": "date"}),
        }


OrderItemFormSet = forms.inlineformset_factory(
    Order,
    OrderItem,
    fields=["service", "name", "description", "price"],
    extra=1,
    can_delete=True,
)