from django.db import models # type: ignore
from orders.models import Order
from products.models import Product
from suppliers.models import Supplier  # type: ignore
from django.utils import timezone


class Invoice(models.Model):
    STATUS_CHOICES = [
        ('pending', 'غير مدفوعة'),
        ('partially_paid', 'مدفوعة جزئيًا'),
        ('paid', 'مدفوعة'),
        ('cancelled', 'ملغاة'),
    ]
    supplier         = models.ForeignKey(Supplier, on_delete=models.CASCADE ,related_name="invoices")  # المورد المرتبط بالفاتورة
    orders           = models.ManyToManyField(Order)  # ربط الفاتورة بالطلبات
    invoice_number   = models.CharField(max_length=50, unique=True)  # رقم الفاتورة
    invoice_date     = models.DateField(auto_now_add=True)  # تاريخ الفاتورة
    due_date         = models.DateField(null=True, blank=True)  # تاريخ الاستحقاق
    previous_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # الرصيد السابق
    current_balance  = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # الرصيد الحالي
    paid_amount      = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # المبلغ المدفوع
    remaining_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # المبلغ المتبقي
    total_amount     = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # إجمالي الفاتورة
    status           = models.CharField(max_length=20, choices=STATUS_CHOICES, default='غير مدفوعة')  
    notes            = models.TextField(blank=True, null=True)  
    
    def update_status(self):
        self.remaining_amount = self.total_amount - self.paid_amount  # حساب المبلغ المتبقي تلقائيًا
        if self.remaining_amount <= 0:
            self.status = 'مدفوعة' 
        elif self.paid_amount > 0:
            self.status = 'مدفوعة جزئيًا'
        else:
            self.status = 'غير مدفوعة'
        self.save()
        
        def save(self, *args, **kwargs):
            """ تحديث البيانات المالية عند الحفظ """
            self.remaining_amount = self.total_amount - self.paid_amount
            self.update_status()  # تحديث الحالة تلقائيًا
            super().save(*args, **kwargs)
            
        def __str__(self):
            return f"فاتورة {self.invoice_number} - {self.supplier.user} - {self.status}"


class InvoiceItem(models.Model):
    invoice          = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="items")  # ربط الفاتورة بالمنتجات
    product_name = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="invoices")
    quantity         = models.PositiveIntegerField(default=1)  # الكمية
    unit_price       = models.DecimalField(max_digits=10, decimal_places=2)  #     
    total_price      = models.DecimalField(max_digits=10, decimal_places=2)  # إجمالي السعر
    expired_quantity = models.IntegerField(default=0)  # ✅ عدد المنتجات منتهية الصلاحية

    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product_name} - {self.invoice.invoice_number}"

class InvoicePayment(models.Model):
    Payment_Method = [
        ('cash', 'نقدي'),
        ('bank_transfer', 'تحويل بنكي'),
        ('credit_card', 'بطاقة ائتمان')
    ]
    invoice        = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="payments")
    amount         = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date   = models.DateTimeField(default=timezone.now)
    payment_method = models.CharField(max_length=50, choices=Payment_Method , default='تحويل بنكي')
    notes          = models.TextField(blank=True, null=True)
    
    def save(self, *args, **kwargs):
        """ عند حفظ الدفع، يتم تحديث الفاتورة تلقائيًا """
        super().save(*args, **kwargs)  # حفظ الدفع
        self.invoice.paid_amount += self.amount
        self.invoice.save()  # تحديث الفاتورة تلقائيًا

    def __str__(self):
        return f"Payment of {self.amount} for {self.invoice.invoice_number}"