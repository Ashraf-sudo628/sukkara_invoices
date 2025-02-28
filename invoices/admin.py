from django.contrib import admin # type: ignore
from .models import *

admin.site.register(Invoice)
admin.site.register(InvoiceItem)
admin.site.register(InvoicePayment)


# Register your models here.
