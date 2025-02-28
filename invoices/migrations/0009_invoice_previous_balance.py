# Generated by Django 4.2.19 on 2025-02-25 12:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('invoices', '0008_alter_invoiceitem_expired_quantity'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoice',
            name='previous_balance',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
    ]
