from django.core.management.base import BaseCommand
from invoices.tasks import *

class Command(BaseCommand):
    help = "إنشاء فواتير الموردين اليومية"

    def handle(self, *args, **kwargs):
        generate_daily_invoice()
        self.stdout.write(self.style.SUCCESS("✅ تم إنشاء الفواتير بنجاح!"))
