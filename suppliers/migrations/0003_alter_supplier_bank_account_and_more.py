# Generated by Django 4.2.19 on 2025-02-17 19:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('suppliers', '0002_alter_supplier_bank_account'),
    ]

    operations = [
        migrations.AlterField(
            model_name='supplier',
            name='bank_account',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='supplier',
            name='phone_number',
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
    ]
