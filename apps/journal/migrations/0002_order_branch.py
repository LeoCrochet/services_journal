import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0001_initial"),
        ("journal", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="branch",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="orders",
                to="accounts.branch",
                verbose_name="Площадка",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="order",
            name="number_seq",
            field=models.IntegerField(blank=True, null=True, verbose_name="Порядковый номер"),
        ),
    ]
