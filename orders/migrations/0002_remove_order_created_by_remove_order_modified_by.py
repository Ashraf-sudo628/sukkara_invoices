# Generated by Django 4.2.19 on 2025-02-19 15:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='created_by',
        ),
        migrations.RemoveField(
            model_name='order',
            name='modified_by',
        ),
    ]
