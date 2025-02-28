from django.contrib import admin # type: ignore
from .models import * # type: ignore


class SupplierAdmin(admin.ModelAdmin):
        list_display = ('name', 'company_name','email' ,'phone_number', 'banck_account_number')
admin.site.register(Supplier)


 

# Register your models here.
