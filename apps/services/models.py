from django.db import models


class Service(models.Model):
    kod = models.CharField("Код", max_length=10, blank=True)
    name = models.CharField("Наименование услуги", max_length=150)
    description = models.TextField("Содержание", blank=True)
    price = models.DecimalField("Цена", max_digits=10, decimal_places=2, default=0)

    class Meta:
        verbose_name = "Услуга"
        verbose_name_plural = "Услуги"
        ordering = ["name"]

    def __str__(self):
        return self.name