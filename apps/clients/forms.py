from django import forms

from .models import Client


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = [
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
            "birth_date": forms.DateInput(attrs={"type": "date"}),
            "document_issue_date": forms.DateInput(attrs={"type": "date"}),
            "registration_period": forms.DateInput(attrs={"type": "date"}),
        }