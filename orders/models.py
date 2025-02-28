from django.db import models
from products.models import Product
from suppliers.models import Supplier
from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings

class Order(models.Model):
    supplier    = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='orders')
    order_date  = models.DateField(auto_now_add=True)
    notes       = models.TextField(blank=True, null=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # إجمالي السعر لجميع المنتجات
    created_at  = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    
    
    def calculate_total_price(self):
        self.total_price = sum(item.total_price for item in self.items.all())
        self.save()
    
    def __str__(self):
        return f"طلب رقم {self.id} من {self.supplier.company_name}"

class OrderItem(models.Model):
    order        = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product_name = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="orders")
    quantity     = models.PositiveIntegerField()
    price        = models.DecimalField(max_digits=10, decimal_places=2)
    expiry_period= models.IntegerField(default=0 ,verbose_name="مدة انتهاء الصلاحية")    
    total_price  = models.DecimalField(max_digits=10, decimal_places=2, editable=False)  # إجمالي السعر للمنتج الواحد
    
    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.price  # حساب السعر الإجمالي تلقائيًا
        super().save(*args, **kwargs)
        if self.order:  # ✅ تأكد أن الطلب موجود قبل تحديث السعر
            self.order.calculate_total_price()  
    
    def __str__(self):
        return f"{self.product_name}"