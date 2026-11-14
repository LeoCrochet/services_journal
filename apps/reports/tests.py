from datetime import date
from io import BytesIO
from urllib.parse import unquote

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from docx import Document

from apps.accounts.models import Branch
from apps.clients.models import Client
from apps.journal.models import Order, OrderItem

from .docx_zayavka import _full_address, build_zayavka_docx
from .exporters import export_clients_to_excel, export_orders_to_excel


class ExportTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.branch = Branch.objects.get(code="TLT")
        cls.branch.signer_name = "Петров Петр Петрович"
        cls.branch.signer_position = "Менеджер"
        cls.branch.save(update_fields=["signer_name", "signer_position"])
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

    def test_zayavka_docx(self):
        order = Order.objects.create(
            branch=self.branch,
            number="ТЛТ-000002",
            document_date=date(2026, 1, 1),
            client=Client.objects.create(
                branch=self.branch,
                fio="Иванов Иван Иванович",
                birth_date=date(1990, 5, 15),
                gender="м",
                citizenship="Узбекистан",
                document_type="Паспорт",
                document_series="AA",
                document_number="1234567",
                document_issue_date=date(2020, 2, 3),
                document_issued_by="МВД",
                region="Самарская",
                district="Сызранский",
                locality="Сызрань",
                street="50 лет Октября",
                house="70",
                apartment="130",
                registration_period=date(2026, 11, 15),
                phone="89276185650",
            ),
        )
        OrderItem.objects.create(order=order, name="Тестирование (патент)", description="Описание услуги", price=4500)

        buf = build_zayavka_docx(order)
        self.assertIsInstance(buf, BytesIO)

        doc = Document(buf)
        text = "\n".join(
            p.text for p in doc.paragraphs if p.text.strip()
        )
        table_text = "\n".join(
            c.text for row in doc.tables[1].rows for c in row.cells
        )

        self.assertIn("Иванов Иван Иванович", text)
        self.assertIn("Узбекистан", text)
        self.assertIn("Тестирование (патент)", table_text)

        table = doc.tables[1]
        self.assertEqual(len(table.rows), 3)  # заголовок + услуга + итого
        self.assertIn("Итого", (c.text for row in table.rows for c in row.cells))

        self.assertNotIn("шаблон", text.lower())

        # Один заголовок с номером заявки вместо двух
        self.assertIn("Заявка №ТЛТ-000002", text)
        self.assertEqual(text.count("Заявка"), 1)

        # Пояснение под ФИО удалено
        self.assertNotIn("(ФИО физического лица, полностью)", text)

        # Подписи полей с двоеточием и форматированный адрес
        self.assertIn("пол: м", text)
        self.assertIn("гражданство: Узбекистан", text)
        self.assertIn("дата выдачи: 03.02.2020", text)
        self.assertIn("кем выдан: МВД", text)
        self.assertIn("Самарская область, Сызранский район, г. Сызрань", text)
        self.assertIn("ул. 50 лет Октября д. 70 кв. 130", text)
        self.assertIn("срок регистрации: 15.11.2026", text)
        self.assertIn("контактный телефон: 89276185650", text)

        # Значения из базы подчёркнуты
        runs = [r for p in doc.paragraphs for r in p.runs]
        fio_run = next(r for r in runs if r.text == "Иванов Иван Иванович")
        self.assertTrue(fio_run.underline)
        citizenship_run = next(r for r in runs if r.text == "Узбекистан")
        self.assertTrue(citizenship_run.underline)

        # Подписи заполнены ФИО клиента, подписантом площадки и текущей датой
        today_str = date.today().strftime("%d.%m.%Y")
        signer = f"{self.branch.signer_name}, {self.branch.signer_position}"
        self.assertIn(f"Заявку принял: {signer}\t(подпись)\t{today_str}", text)
        self.assertIn(f"Заказчик: Иванов Иван Иванович\t(подпись)\t{today_str}", text)
        self.assertIn(signer, text)
        self.assertIn(today_str, text)

    def test_full_address_without_district(self):
        client = Client.objects.create(
            branch=self.branch,
            fio="Без района",
            region="Самарская",
            locality="Сызрань",
            street="50 лет Октября",
            house="70",
            apartment="130",
        )
        address = _full_address(client)
        self.assertNotIn(", ,", address)
        self.assertNotIn("район", address)
        self.assertIn("г. Сызрань", address)

    def test_order_docx_filename(self):
        user = User.objects.create_user("docx_su", is_superuser=True)
        self.client.force_login(user)
        url = reverse("reports:order_docx", args=[self.order.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        header_value = response["Content-Disposition"]
        decoded = unquote(header_value.split("filename*=UTF-8''")[-1])
        self.assertIn("Заявка №ТЛТ-000001", decoded)
