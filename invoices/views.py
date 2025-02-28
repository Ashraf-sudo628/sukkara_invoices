from decimal import Decimal
from django.contrib import messages
from django.forms import modelformset_factory
from django.shortcuts import render,redirect # type: ignore
from .models import * # type: ignore
from .forms import * # type: ignore
from django.contrib.auth.decorators import login_required # type: ignore
from django.shortcuts import get_object_or_404, redirect
from django.utils.timezone import now
from invoices.models import Order, Supplier
from invoices.tasks import generate_daily_invoice


# @login_required
# def create_invoice(request):
    
#     if request.method == 'POST':
#         invoice_form  = InvoiceForm(request.POST)
#         item_form   = InvoiceItemForm(request.POST)

#         if invoice_form.is_valid() and item_form.is_valid():
#             invoice          = invoice_form.save(commit=False)
#             invoice.supplier = request.user
#             invoice.total_amount = invoice.current_balance
#             invoice.remaining_amount = invoice.current_balance - invoice.paid_amount
#             invoice.save()
            
#             item = item_form.save(commit=False)
#             item.invoice = invoice
#             item.total_price = item.quantity * item.unit_price
#             item.save()
            
#             return redirect('invoice/invoice_list')  # بعد الحفظ، يعاد التوجيه إلى قائمة الفواتير
        
#         else:
#             invoice_form = InvoiceForm()
#             item_form = InvoiceItemForm()
        
#         context={
#             'invoice_form': invoice_form,
#             'item_form': item_form,
#         }
            
#         return render(request, 'invoice/create_invoice.html', context)

def create_invoice_view(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    supplier = order.supplier  # استخراج المورد من الطلب
    today = now().date()

    # تحقق مما إذا كانت هناك فاتورة اليوم لهذا المورد
    existing_invoice = supplier.invoices.filter(invoice_date=today).first()

    if not existing_invoice:
        generate_daily_invoice(supplier)  # إنشاء الفاتورة لهذا المورد

    return redirect('admin_dashboard')  # إعادة التوجيه إلى قائمة الطلبات

def invoice_detail(request, invoice_id):
    today = now().date()  # التاريخ الحالي
    calculated_total_price = 0
    invoice = get_object_or_404(Invoice, id=invoice_id)
    
    for item in invoice.items.all():
        if item.expired_quantity and item.expired_quantity > 0:
            calculated_total_price = item.expired_quantity * item.unit_price
    
    if request.user.is_staff:
        dashboard_url = 'admin_dashboard'
    else:
        dashboard_url = 'dashboard'
    form = PaymentForm()  # تأكد من تعريف النموذج

    context = {
        'form':form,
        'invoice': invoice,
        'dashboard_url': dashboard_url,
        'calculated_total_price':0
    }
    return render(request, 'invoice/invoice_detail.html', context)
@login_required
def invoice_list_supplier(request):
    try:
        supplier = request.user.supplier  # جلب كائن المورد المرتبط بالمستخدم
        invoices = Invoice.objects.filter(supplier=supplier)
    except AttributeError:
        messages.error(request, "أنت لست موردًا!")
        return redirect('dashboard')  # إعادة توجيه غير الموردين
    context = {'invoices': invoices}
    return render(request, 'invoice/invoice_list_supplier.html', context)

def invoice_list(request):
    if request.user.is_staff:
        invoices = Invoice.objects.all()
    else:
        try:
            supplier = request.user.supplier  # جلب المورد المرتبط بالمستخدم
            invoices = Invoice.objects.filter(supplier=supplier)  # عرض فواتيره فقط
        except AttributeError:
            invoices = []  # إذا لم يكن المورد مسجلاً، لا تعرض أي فواتير
    context = {
        'invoices': invoices,
        }
    return render(request, 'invoice/invoice_list.html', context)

def edit_daily_invoice(request, invoice_id):
    # جلب الفاتورة اليومية بناءً على معرّفها
    invoice = get_object_or_404(Invoice, id=invoice_id)
    supplier = invoice.supplier  # جلب المورد المرتبط بالفاتورة

    # جلب المنتجات الأصلية بدون تعديل
    original_items = InvoiceItem.objects.filter(invoice=invoice)
    
    # إنشاء Formset لإضافة المنتجات المنتهية الصلاحية فقط
    ExpiredProductFormSet = modelformset_factory(InvoiceItem, form=ExpiredProductForm, extra=1, can_delete=True)
    
    
    if request.method == 'POST':
        formset = ExpiredProductFormSet(request.POST, queryset=InvoiceItem.objects.filter(invoice=invoice, quantity=0),form_kwargs={'supplier': supplier})
        
        if formset.is_valid():
            instances = formset.save(commit=False)
            total_expired_cost = 0
            
            for item in instances:
                item.invoice = invoice
                item.total_price= item.expired_quantity * item.unit_price
                total_expired_cost += item.total_price 
                item.save()  
            formset.save_m2m()
            # تحديث إجمالي الفاتورة بعد خصم المنتجات المنتهية الصلاحية
            invoice.total_amount -= total_expired_cost
            invoice.remaining_amount = invoice.total_amount - invoice.paid_amount
            invoice.current_balance -= total_expired_cost
            invoice.save()
            
            supplier.current_balance -= total_expired_cost
            supplier.save() 
            messages.success(request, "the invoice has been updated successfully. Expired products have been removed.")
            return redirect('invoice_detail', invoice_id=invoice.id)
        else:
            messages.error(request, "there are some errors in data.")
    else:
        formset = ExpiredProductFormSet(queryset=InvoiceItem.objects.filter(invoice=invoice, quantity=0), form_kwargs={'supplier': supplier})
    context = {
        'invoice': invoice,
        'original_items': original_items,
        'formset': formset,
        
    }
    return render(request, 'invoice/edit_daily_invoice.html', context)
def add_payment(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)
    supplier = invoice.supplier  # جلب المورد المرتبط بالفاتورة

    if request.method == "POST":
        form = PaymentForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']

            if amount > 0 and amount <= invoice.remaining_amount:
                # إنشاء سجل الدفع
                InvoicePayment.objects.create(invoice=invoice, amount=amount)

                # تحديث بيانات الفاتورة
                invoice.paid_amount = amount
                invoice.remaining_amount -= amount
                invoice.current_balance -= amount
                
                # تحديث حالة الفاتورة
                if invoice.remaining_amount == 0:
                    invoice.status = "مدفوعة"
                else:
                    invoice.status = "مدفوعة جزئيًا"
                    
                invoice.save()
                # تحديث الرصيد السابق للمورد (إذا تبقى مبلغ في الفاتورة)
                if invoice.remaining_amount > 0:
                    supplier.previous_balance = invoice.remaining_amount  # المبلغ المتبقي من الفاتورة الحالية
                    supplier.current_balance -= amount
                else:
                    supplier.previous_balance = 0  # لا يوجد رصيد سابق
                    supplier.current_balance -= amount
                    
                    
                # supplier.current_balance += supplier.previous_balance  # تحديث الرصيد الحالي ليكون الرصيد السابق

                supplier.save()
                
                messages.success(request, "تمت إضافة الدفعة بنجاح.")
                return redirect('invoice_detail', invoice_id=invoice.id)
            else:
                messages.error(request, "المبلغ المدفوع يجب أن يكون أكبر من 0 وأقل من أو يساوي المبلغ المتبقي.")
        else:
            messages.error(request, "يرجى إدخال مبلغ صالح.")
    
    else:
        form = PaymentForm()  # عرض نموذج فارغ في حالة طلب GET

    return render(request, 'invoice/invoice_detail.html', {'form': form, 'invoice': invoice})