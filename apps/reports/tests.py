from datetime import date

from django.test import TestCase

from apps.accounts.models import Branch
from apps.clients.models import Client
from apps.journal.models import Order, OrderItem

from .exporters import export_clients_to_excel, export_orders_to_excel


class ExportTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.branch = Branch.objects.get(code="TLT")
        cls.client_a = Client.objects.create(branch=cls.branch, fio="Экспорт Клиент")
        cls.order = Order.objects.create(branch=cls.branch, number="ТЛТ-000001", document_date=date.today(), client=cls.client_a)
        OrderItem.objects.create(order=cls.order, name="Услуга", price=50)

    def test_clients_excel(self):
        response = export_clients_to_excel([self.client_a])
        self.assertEqual(response.status_code, 200)
        self.assertIn("spreadsheetml", response["Content-Type"])

    def test_orders_excel(self):
        response = export_orders_to_excel([self.order])
        self.assertEqual(response.status_code, 200)
        self.assertIn("spreadsheetml", response["Content-Type"])
