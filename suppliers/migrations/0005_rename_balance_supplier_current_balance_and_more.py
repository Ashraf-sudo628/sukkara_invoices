# Generated by Django 4.2.19 on 2025-02-22 14:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('suppliers', '0004_supplier_balance'),
    ]

    operations = [
        migrations.RenameField(
            model_name='supplier',
            old_name='balance',
            new_name='current_balance',
        ),
        migrations.AddField(
            model_name='supplier',
            name='previous_balance',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
    ]
