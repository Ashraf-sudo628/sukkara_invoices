# Generated by Django 4.2.19 on 2025-02-20 10:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0002_remove_order_created_by_remove_order_modified_by'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='balance',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
    ]
