from collections import defaultdict
from datetime import date , timedelta
from django.utils.timezone import now
from .models import *
from orders.models import *
from suppliers.models import *
from django.db.models import Sum

def generate_daily_invoice(supplier):
    today = date.today()
    
    # التحقق مما إذا كان هناك فاتورة سابقة لهذا المورد في اليوم
    invoice, created = Invoice.objects.get_or_create(
        supplier=supplier,
        invoice_date=today,
        defaults={
            "invoice_number": f"INV-{supplier.id}-{today.strftime('%Y%m%d')}",
            "total_amount": 0,
            "paid_amount": 0,
            "remaining_amount": 0,
            "previous_balance" : supplier.previous_balance  # تحميل الرصيد السابق من المورد  # تحميل الرصيد السابق من المورد
        },
    )

    if not created:
        print(f"  {invoice.invoice_number}  invoice exist will updated.")
    # جلب جميع الطلبات الخاصة بالمورد اليوم
    orders = Order.objects.filter(supplier=supplier, order_date=today)
    total_invoice_amount = sum(order.total_price for order in orders)
    
    if not orders.exists():
        return None
    
        #  تجميع كل المنتجات من الطلبات
    product_summary = defaultdict(lambda: {"quantity": 0, "unit_price": 0, "total_price": 0,"expired_quantity": 0})

    for order in orders:
        # حساب الفرق بين تاريخ الطلب واليوم الحالي
        days_passed = (date.today() - order.order_date).days
        for order_item in order.items.all():
            product_name = order_item.product_name
            product_summary[product_name]["quantity"] += order_item.quantity
            product_summary[product_name]["unit_price"] = order_item.price
            product_summary[product_name]["total_price"] += order_item.quantity * order_item.price
            
            print("summary:", dict(product_summary))

            # حساب المنتجات منتهية الصلاحية
            if days_passed > order_item.expiry_period:
                    product_summary[product_name]["expired_quantity"] += order_item.quantity  
            
    total_invoice_amount = 0  # إجمالي قيمة الفاتورة
    expired_products_cost = 0  # تكلفة المنتجات منتهية الصلاحية
    existing_items = {item.product_name: item for item in invoice.items.all()}  

    for product_name, details in product_summary.items():
    # البحث عن المنتج داخل الفاتورة وتحديثه أو إنشاؤه
        invoice_item, item_created = InvoiceItem.objects.get_or_create(
            invoice=invoice,
            product_name=product_name,
            defaults={
                "quantity": details["quantity"],
                "unit_price": details["unit_price"],
                "total_price": 0,
                "expired_quantity": details["expired_quantity"],
            }
        )
        # ✅ تحديث الكمية والسعر الإجمالي
        invoice_item.quantity = details["quantity"]
        invoice_item.total_price = details["quantity"] * details["unit_price"]
        invoice_item.expired_quantity = details["expired_quantity"]
        invoice_item.save()
        
        total_invoice_amount += invoice_item.total_price
        
        if invoice_item.expired_quantity > 0:
            expired_products_cost += invoice_item.unit_price * invoice_item.expired_quantity 
    
    # ✅ حساب القيمة الجديدة بعد استبعاد المنتجات المنتهية الصلاحية
    new_invoice_total = total_invoice_amount - expired_products_cost

    # ✅ حساب الفرق بين القيمة الجديدة والقيمة السابقة للفاتورة
    difference = new_invoice_total - invoice.total_amount
    
    print("difference:" ,difference)
        # ✅ تحديث إجمالي الفاتورة والمبالغ المالية
    invoice.total_amount = new_invoice_total
    invoice.remaining_amount = invoice.total_amount - invoice.paid_amount
    invoice.current_balance = difference + invoice.previous_balance
    
    invoice.save()

    # ✅ تحديث الرصيد الحالي للمورد: (الرصيد السابق + إجمالي الفاتورة الجديدة)
    supplier.current_balance +=  difference
    supplier.save()
    
    print(f"  {'Updated' if not created else 'Created'} Invoice {invoice.invoice_number} with total {invoice.total_amount} for supplier {supplier.user.username}")

    return invoice

def update_invoice_after_deletion(order):
    today = date.today()
    
    # ✅ جلب الفاتورة الخاصة بالمورد لهذا اليوم
    invoice = Invoice.objects.filter(supplier=order.supplier, invoice_date=today).first()
    
    if not invoice:
        return  # لا توجد فاتورة لهذا المورد، لا حاجة للتحديث
    print(f" update invoice after delete product or order {invoice.invoice_number} ...")
    # ✅ حذف المنتجات التي لم تعد موجودة في أي طلب
    for invoice_item in invoice.items.all():
        product_name = invoice_item.product_name

        # ✅ تحقق مما إذا كان المنتج لا يزال موجودًا في أي طلب اليوم
        existing_order_items = OrderItem.objects.filter(
            order__supplier=order.supplier, 
            order__order_date=today, 
            product_name=product_name
        )

        if not existing_order_items.exists():
            print(f" delete product from invoice{product_name}  .")
            invoice_item.delete()  # ✅ حذف العنصر من الفاتورة

    # ✅ إعادة حساب إجمالي الفاتورة
    total_invoice_amount = sum(item.total_price for item in invoice.items.all())

    # ✅ تحديث الفاتورة إذا كان هناك منتجات متبقية
    if total_invoice_amount > 0:
        invoice.total_amount = total_invoice_amount
        invoice.remaining_amount = total_invoice_amount
        invoice.save()
        print(f"✅   invoice updated {invoice.invoice_number}.")

    else:
        print(f" delete invoice as it's empty {invoice.invoice_number}.")

        # ✅ إذا أصبحت الفاتورة فارغة، يتم حذفها
        invoice.delete()


def update_invoice_after_product_deletion(order, deleted_products):
    """تحديث الفاتورة بعد حذف منتجات من الطلب."""
    if not deleted_products:
        return  # ✅ لا يوجد شيء لحذفه

    today = date.today()
    invoice = Invoice.objects.filter(supplier=order.supplier, invoice_date=today).first()

    if not invoice:
        return


    for product_name in deleted_products:
        invoice_item = InvoiceItem.objects.filter(invoice=invoice, product_name=product_name).first()
        
        if invoice_item:
            invoice_item.delete()
    # ✅ تحديث إجمالي المبلغ بعد الحذف
    order.total_price = sum(item.quantity * item.price for item in order.items.all())
    order.save()
    # ✅ تحديث الفاتورة بعد حذف المنتجات
    total_invoice_amount = sum(item.total_price for item in invoice.items.all())

    if total_invoice_amount > 0:
        invoice.total_amount = total_invoice_amount
        invoice.remaining_amount = total_invoice_amount
        invoice.save()
    else:
        invoice.delete()