
from pyexpat.errors import messages
from django.shortcuts import render ,redirect
from .models import *
from .forms import *
from suppliers.models import *
from django.forms import formset_factory, modelformset_factory
from django.contrib.auth.decorators import login_required ,user_passes_test
from suppliers.views import *
from invoices.tasks import *
from django.shortcuts import render, get_object_or_404
from .models import Order
from django.db import transaction
from datetime import date

def create_order(request):
    supplier = Supplier.objects.get(user=request.user)
    products = Product.objects.filter(supplier=supplier)
    today = now().date()

    order, created = Order.objects.get_or_create(supplier=supplier, order_date=today)

    item_form = OrderItemForm(supplier=supplier)

    if request.method == 'POST':
        item_form = OrderItemForm(request.POST, request.FILES, supplier=supplier)
        
        if item_form.is_valid():
            product = item_form.cleaned_data['product_name']
            quantity = item_form.cleaned_data['quantity']

            # التحقق إذا كان المنتج موجود في نفس الطلب
            existing_item = OrderItem.objects.filter(order=order, product_name=product).first()
            
            if existing_item:
                # لو المنتج موجود اجمع الكمية وحدث السعر الكلي
                existing_item.quantity += quantity
                existing_item.total_price = existing_item.quantity * existing_item.price
                existing_item.save()
            else:
                # لو المنتج مش موجود ضيفه جديد
                item = item_form.save(commit=False)
                item.order = order
                item.price = product.selling_price
                item.total_price = quantity * item.price
                item.save()

            update_invoice_after_deletion(order)
            generate_daily_invoice(supplier)

            # عرض المنتجات في الجدول بدون تحديث الصفحة
            order_items = OrderItem.objects.filter(order=order).prefetch_related('product_name')
            data = [{'product_name': item.product_name.name, 'price': item.price, 'quantity': item.quantity, 'total_price': item.total_price} for item in order_items]
            
            return JsonResponse(data, safe=False)
        else:
            print("item_form errors:", item_form.errors)

    order_items = OrderItem.objects.filter(order=order).prefetch_related('product_name')

    context = {
        'item_form': item_form,
        'order_items': order_items,
        'products': products,
    }
    return render(request, 'orders/create_order.html', context)  

def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    
    if request.user.is_staff:
        dashboard_url = 'admin_dashboard'
    else:
        dashboard_url = 'dashboard'
    context = {
        'order': order,
        'dashboard_url': dashboard_url,
    }
    return render(request, 'orders/order_detail.html', context)

def edit_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    supplier = order.supplier
    old_total = order.total_price
    
    OrderItemFormSet = modelformset_factory(
        OrderItem, form=OrderItemForm,
        fields=('product_name', 'price', 'quantity', 'expiry_period'),
        extra=0, can_delete=True,
    )

    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order)
        formset = OrderItemFormSet(request.POST, request.FILES, queryset=OrderItem.objects.filter(order=order))
        # formset = OrderItemFormSet(request.POST, instance=order)
        print("🚀 Full formset data received:", request.POST)
        if form.is_valid() and formset.is_valid():
            order = form.save()
            print("✅  order saved  :", order)   
            
            deleted_products = []
            for form in formset:
                print("🔎 Checking form data:", form.cleaned_data)  # ✅ تحقق من البيانات الواردة
                if form.cleaned_data and any(form.cleaned_data.values()):  # ✅ التأكد أن النموذج يحتوي على بيانات فعلية

                    print("📌  edited item detail :", form.cleaned_data)
                    
                    if form.cleaned_data.get('DELETE', False):
                        product_name = form.cleaned_data.get('product_name')
                        deleted_products.append(product_name)
                        if form.instance.pk:
                            print("🆔 Form instance PK:", form.instance.pk)
                            form.instance.delete()
                    else:
                        if not form.instance.pk:  # 🔥 هذا منتج جديد
                            print("🆕 New product detected:", form.cleaned_data.get("product_name"))
                        order_item = form.save(commit=False)
                        order_item.order = order
                        order_item.save()
                        print(" Saving new product:", order_item.product_name)    

            new_total = sum(item.price * item.quantity for item in order.items.all())
            order.total_price = new_total
            order.save()

            print(f"Supplier balance after add or delete products {new_total} to supplier {supplier.user.username}...")

            # difference = old_total - new_total
            # supplier.current_balance -= difference
            # supplier.save()

            update_invoice_after_product_deletion(order, deleted_products)

            # ✅ تحديث الفاتورة بعد التعديل
            generate_daily_invoice(supplier)
            if request.user.is_staff:
                return redirect('order-list')
            else:
                return redirect('order-list-supplier')

        else:
            print(form.errors)
            print(formset.errors)

    else:
        form = OrderForm(instance=order)
        formset = OrderItemFormSet(queryset=OrderItem.objects.filter(order=order))
    # إحضار جميع المنتجات الخاصة بالمورد
    available_products = supplier.products.all()
    context = {
        'form': form,
        'formset': formset,
        'order': order,
        'available_products' :available_products,
        
    }
    return render(request, 'orders/edit_order.html', context)

def delete_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, supplier=request.user.supplier)

    print(f"🗑️  delete order {order.id} for supplier {order.supplier.user.username}...")
    
    supplier = order.supplier
    supplier.current_balance -= order.total_price
    supplier.save()
    
    order.delete()  # ✅ حذف الطلب من قاعدة البيانات
    update_invoice_after_deletion(order)
    messages.success(request, "order deleted successfully!")
        
    return redirect('order-list-supplier')  # إعادة التوجيه بعد الحذف
@login_required
def order_list_supplier(request):
    try:
        supplier = request.user.supplier  # جلب كائن المورد المرتبط بالمستخدم
        orders = Order.objects.filter(supplier=supplier,total_price__gt=0)
    except AttributeError:
        messages.error(request, "أنت لست موردًا!")
        return redirect('dashboard')  # إعادة توجيه غير الموردين
    context = {'orders': orders}
    return render(request, 'orders/order_list_supplier.html', context)

def order_list(request):
    if request.user.is_staff:
        orders = Order.objects.filter(total_price__gt=0)
    else:
        try:
            supplier = request.user.supplier  # جلب المورد المرتبط بالمستخدم
            orders = Order.objects.filter(supplier=supplier)  # عرض فواتيره فقط
        except AttributeError:
            invoices = []  # إذا لم يكن المورد مسجلاً، لا تعرض أي فواتير
    print()
    context = {'orders': orders}
    return render(request, 'orders/order_list.html', context)

    

