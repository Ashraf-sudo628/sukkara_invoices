from django.db import models # type: ignore
from django.contrib.auth.models import User # type: ignore


class Supplier(models.Model):
    user             = models.OneToOneField(User, on_delete=models.CASCADE)
    company_name     = models.CharField(max_length=255)
    email            = models.EmailField(max_length=254, blank=True, null=True)
    phone_number     = models.CharField(max_length=15, blank=True, null=True)  # إضافة رقم الهاتف
    bank_account     = models.CharField(max_length=50,blank=True, null=True)
    address          = models.TextField(blank=True, null=True )  # العنوان
    previous_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # الرصيد السابق
    current_balance  = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # الرصيد الحالي
    

    def __str__(self):
        return self.company_name
