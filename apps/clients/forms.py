from django import forms

from .models import Client


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = [
            "branch",
            "kod",
            "fio",
            "birth_date",
            "gender",
            "citizenship",
            "document_type",
            "document_series",
            "document_number",
            "document_issue_date",
            "document_issued_by",
            "region",
            "district",
            "locality",
            "street",
            "house",
            "building",
            "apartment",
            "registration_period",
            "phone",
        ]
        widgets = {
            "birth_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "document_issue_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "registration_period": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if isinstance(field, (forms.ModelChoiceField, forms.ChoiceField)):
                css_class = "form-select"
            else:
                css_class = "form-control"
            field.widget.attrs.setdefault("class", css_class)
