from django.db import models

from apps.clients.models import Client
from apps.services.models import Service


class Order(models.Model):
    number = models.CharField("Номер", max_length=20, blank=True)
    document_date = models.DateField("Дата документа")
    client = models.ForeignKey(
        Client,
        verbose_name="Клиент",
        on_delete=models.PROTECT,
        related_name="orders",
    )
    created_at = models.DateTimeField("Создан", auto_now_add=True)
    updated_at = models.DateTimeField("Обновлён", auto_now=True)

    class Meta:
        verbose_name = "Запись журнала"
        verbose_name_plural = "Журнал регистрации услуг"
        ordering = ["-document_date", "-id"]

    def __str__(self):
        return f"№{self.number} от {self.document_date} — {self.client}"

    @property
    def total(self):
        return sum(item.price for item in self.items.all())


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        verbose_name="Запись журнала",
        on_delete=models.CASCADE,
        related_name="items",
    )
    service = models.ForeignKey(
        Service,
        verbose_name="Услуга",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="order_items",
    )
    name = models.CharField("Наименование услуги", max_length=150)
    description = models.TextField("Содержание", blank=True)
    price = models.DecimalField("Цена", max_digits=10, decimal_places=2, default=0)

    class Meta:
        verbose_name = "Оказанная услуга"
        verbose_name_plural = "Оказанные услуги"
        ordering = ["id"]

    def __str__(self):
        return self.name