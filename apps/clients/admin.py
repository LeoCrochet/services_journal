from django.contrib import admin

from .models import Client


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("kod", "fio", "birth_date", "document_type", "phone")
    search_fields = ("fio", "kod", "phone")
    list_filter = ("gender", "document_type", "citizenship")