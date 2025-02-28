from django.db import models
from suppliers.models import Supplier
from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings

class Product(models.Model):
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name="products")
    name = models.CharField(max_length=255, verbose_name="اسم المنتج")
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="سعر الشراء")
    selling_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="سعر البيع",null=True, blank=True, )
    expiry_period = models.IntegerField(default=0 ,verbose_name="مدة انتهاء الصلاحية")
    notes = models.TextField(blank=True, null=True, verbose_name="ملاحظات")


    def __str__(self):
        return f"{self.name}"
