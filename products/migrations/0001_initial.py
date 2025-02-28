# Generated by Django 4.2.19 on 2025-02-26 14:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('suppliers', '0005_rename_balance_supplier_current_balance_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Products',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='اسم المنتج')),
                ('purchase_price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='سعر الشراء')),
                ('selling_price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='سعر البيع')),
                ('expiry_date', models.DateField(blank=True, null=True, verbose_name='تاريخ انتهاء الصلاحية')),
                ('notes', models.TextField(blank=True, null=True, verbose_name='ملاحظات')),
                ('supplier', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='products', to='suppliers.supplier')),
            ],
        ),
    ]
