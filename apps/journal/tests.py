from django.contrib.auth.models import User
from django.test import TestCase

from apps.accounts.models import ROLE_OPERATOR, Branch, UserProfile
from apps.clients.models import Client

from .forms import OrderForm, OrderItemFormSet
from .models import Order, OrderItem
from .services import generate_order_number, get_visible_orders


class OrderServicesTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.branch = Branch.objects.get(code="TLT")
        cls.branch2 = Branch.objects.get(code="SZR")

        cls.client_a = Client.objects.create(branch=cls.branch, fio="Первый Клиент")
        cls.client_b = Client.objects.create(branch=cls.branch2, fio="Второй Клиент")

        cls.order1 = Order.objects.create(branch=cls.branch, document_date="2026-01-01", client=cls.client_a)
        cls.order2 = Order.objects.create(branch=cls.branch2, document_date="2026-01-02", client=cls.client_b)

    def test_generate_order_number(self):
        order = Order(branch=self.branch)
        generate_order_number(order)
        self.assertEqual(order.number, "ТЛТ-000001")
        self.assertEqual(order.number_seq, 1)

    def test_generate_order_number_unique_per_branch(self):
        order = Order(branch=self.branch, document_date="2026-01-01", client=self.client_a)
        generate_order_number(order)
        order.save()

        order2 = Order(branch=self.branch, document_date="2026-01-01", client=self.client_a)
        generate_order_number(order2)
        self.assertEqual(order2.number, "ТЛТ-000002")

        order3 = Order(branch=self.branch2, document_date="2026-01-01", client=self.client_b)
        generate_order_number(order3)
        self.assertEqual(order3.number, "СЗР-000001")

    def test_visible_orders_operator_filtered(self):
        user = User.objects.create_user("oper")
        UserProfile.objects.create(user=user, role=ROLE_OPERATOR, branch=self.branch)
        orders = get_visible_orders(user)
        self.assertEqual(list(orders), [self.order1])

    def test_visible_orders_superuser_all(self):
        user = User.objects.create_user("su", is_superuser=True)
        orders = get_visible_orders(user)
        self.assertEqual(orders.count(), 2)

    def test_order_formset_requires_at_least_one_item(self):
        data = {
            "branch": self.branch.pk,
            "number": "",
            "document_date": "2026-01-01",
            "client": self.client_a.pk,
            "items-TOTAL_FORMS": "1",
            "items-INITIAL_FORMS": "0",
            "items-MIN_NUM_FORMS": "0",
            "items-MAX_NUM_FORMS": "1000",
            "items-0-service": "",
            "items-0-name": "",
            "items-0-description": "",
            "items-0-price": "",
        }
        form = OrderForm(data)
        formset = OrderItemFormSet(data)
        self.assertTrue(form.is_valid())
        self.assertFalse(formset.is_valid())
        self.assertIn("Добавьте хотя бы одну услугу.", formset.non_form_errors())
