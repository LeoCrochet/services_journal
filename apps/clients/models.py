from django.db import models

DOCUMENT_TYPES = [
    ("ВНЖ", "ВНЖ"),
    ("Паспорт", "Паспорт"),
    ("Справка", "Справка"),
]


class Client(models.Model):
    GENDER_CHOICES = [("м", "м"), ("ж", "ж")]

    branch = models.ForeignKey(
        "accounts.Branch",
        verbose_name="Площадка",
        on_delete=models.PROTECT,
        related_name="clients",
    )
    kod = models.CharField("Код", max_length=6, blank=True)
    fio = models.CharField("ФИО", max_length=150)
    birth_date = models.DateField("Дата рождения", null=True, blank=True)
    gender = models.CharField("Пол", max_length=1, choices=GENDER_CHOICES, blank=True)
    citizenship = models.CharField("Гражданство", max_length=60, blank=True)

    document_type = models.CharField("Тип документа", max_length=20, choices=DOCUMENT_TYPES, blank=True)
    document_series = models.CharField("Серия", max_length=10, blank=True)
    document_number = models.CharField("Номер", max_length=10, blank=True)
    document_issue_date = models.DateField("Дата выдачи", null=True, blank=True)
    document_issued_by = models.CharField("Кем выдан", max_length=35, blank=True)

    region = models.CharField("Область", max_length=90, blank=True)
    district = models.CharField("Район", max_length=90, blank=True)
    locality = models.CharField("Населённый пункт", max_length=90, blank=True)
    street = models.CharField("Улица", max_length=50, blank=True)
    house = models.CharField("Дом", max_length=10, blank=True)
    building = models.CharField("Корпус", max_length=6, blank=True)
    apartment = models.CharField("Квартира", max_length=6, blank=True)

    registration_period = models.DateField("Срок регистрации", null=True, blank=True)
    phone = models.CharField("Телефон", max_length=14, blank=True)

    created_at = models.DateTimeField("Создан", auto_now_add=True)
    updated_at = models.DateTimeField("Обновлён", auto_now=True)

    class Meta:
        verbose_name = "Клиент"
        verbose_name_plural = "Клиенты"
        ordering = ["fio"]

    def __str__(self):
        return self.fio