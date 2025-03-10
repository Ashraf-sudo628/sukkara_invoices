import datetime
from django.forms import modelformset_factory
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from invoices.tasks import generate_daily_invoice, update_invoice_after_deletion
from orders.forms import OrderForm, OrderItemForm
from orders.models import Order, OrderItem # type: ignore
from .forms import SupplierRegistrationForm ,SupplierEditForm
from django.contrib.auth import login , logout ,get_user_model
from django.contrib.auth.models import User
from invoices.models import *
from django.contrib.auth.decorators import login_required ,user_passes_test
from .models import *
from django.contrib import messages
from django.utils.timezone import now
from datetime import date 
from django.contrib.auth.views import LoginView
from products.models import *
from django.contrib.auth.views import PasswordResetView

def is_admin(user):
    return user.is_staff

class CustomLoginView(LoginView):
    def form_invalid(self, form):
        messages.error(self.request, "اسم المستخدم أو كلمة المرور غير صحيحة.")
        return super().form_invalid(form)

@login_required
def dashboard_redirect(request):
    if request.user.is_staff:
        return redirect('admin_dashboard')
    else:
        return redirect('dashboard')

def supplier_registration(request):
    if request.method == 'POST':
        form = SupplierRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])  # تعيين كلمة المرور
            
            user.save()

            Supplier.objects.create(
                user=user,
                company_name=user.username,  # افتراضيًا: اسم الشركة = اسم المستخدم
                email=user.email,  # حفظ البريد الإلكتروني في المورد
                bank_account="",  # بيانات افتراضية يمكن تغييرها لاحقًا
                phone_number="",
                address=""
            )
            login(request, user)  # تسجيل الدخول بالمستخدم اذا تم التسجيل بنجاح
            return redirect('/dashboard/')  # إعادة توجيه عند نجاح التسجيل
    else:
        form = SupplierRegistrationForm()  # إنشاء نموذج فارغ عند الطلب GET

    # إعادة النموذج دائمًا، سواء كان صالحًا أو غير صالح
    return render(request, 'registration/register.html', {'form': form})

def user_logout(request):
    logout(request)
    return redirect('login')  # تحويل المستخدم إلى صفحة تسجيل الدخول بعد تسجيل الخروج

@login_required
def supplier_edit_profile(request):
    try:
        supplier = Supplier.objects.get(user=request.user)  # جلب بيانات المورد المرتبط بالمستخدم
    except Supplier.DoesNotExist:
        messages.error(request, "لا توجد بيانات مورد مرتبطة بحسابك.")
        return redirect('dashboard')

    if request.method == 'POST':
        form = SupplierEditForm(request.POST, instance=supplier)  # استخدم النموذج الصحيح
        if form.is_valid():
            form.save()
            messages.success(request, "تم تحديث بيانات المورد بنجاح.")
            return redirect('dashboard')
    else:
        form = SupplierEditForm(instance=supplier)  # تمرير البيانات الحالية للمورد

    return render(request, 'suppliers/edit_profile.html', {'form': form})
        
@login_required
def supplier_dashboard(request):
    today = now().date()  # تحديد اليوم الحالي
    try:
        supplier = Supplier.objects.get(user=request.user)  # جلب بيانات المورد المرتبط بالمستخدم
        orders   = Order.objects.filter(supplier=supplier , order_date=today,total_price__gt=0)  # جلب الطلبات الخاصة به
    except Supplier.DoesNotExist:
        supplier = None
    print(",,,,,,,,,,,,,",supplier)
    invoices = Invoice.objects.filter(supplier=supplier ,invoice_date=today)
    
    context = {
        'supplier': supplier,
        'invoices': invoices,
        'orders'  : orders
    }
    return render(request, 'suppliers/dashboard.html', context)

@login_required
@user_passes_test(is_admin)  # يمنع غير المدير من الوصول
def admin_dashboard(request):
    today = now().date()  # تحديد اليوم الحالي
    orders = Order.objects.filter(order_date=today,total_price__gt=0).order_by('-created_at')  # جلب كل الطلبات
    
    invoices = Invoice.objects.filter(invoice_date=today).order_by('-invoice_date')  # جلب كل الفوات
    
    order_invoice_status = {}  # تخزين حالة الفاتورة لكل طلب
    for order in orders:
        has_invoice = Invoice.objects.filter(supplier=order.supplier, invoice_date=today).exists()
        order_invoice_status[order.id] = has_invoice

    context = {
        'orders': orders,
        'invoices': invoices,
        'order_invoice_status': order_invoice_status,
    }
    return render(request, 'admin/admin_dashboard.html', context)


def supplier_list(request):
    suppliers = Supplier.objects.exclude(user__is_staff = True)
    context = {'suppliers': suppliers}
    return render(request, 'suppliers/suppliers_list.html', context)

def supplier_detail(request, supplier_id):
    supplier = get_object_or_404(Supplier, id=supplier_id)
    products = Product.objects.filter(supplier = supplier)
    orders   = Order.objects.filter(supplier = supplier)
    invoices = Invoice.objects.filter(supplier = supplier)
    
    context = {
        'supplier': supplier,
        'products': products,
        'orders'  : orders,
        'invoices': invoices,
    }
    return render(request, 'suppliers/supplier_detail.html', context)

@login_required
def create_order_for_supplier(request, supplier_id):
    
    supplier = Supplier.objects.get(id=supplier_id)  # جلب بيانات المورد
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
class CustomPasswordResetView(PasswordResetView):
    def get_success_url(self):
        return ''  # بترجع فاضية عشان يمنع أي Redirect

    def form_valid(self, form):
        email = form.cleaned_data['email']
        User = get_user_model()

        if User.objects.filter(email=email).exists():
            super().form_valid(form)
            return JsonResponse({"message": "✅ تم إرسال رابط إعادة تعيين كلمة المرور إلى بريدك الإلكتروني."}, status=200)
        else:
            return JsonResponse({"error": "❌ البريد الإلكتروني غير مسجل."}, status=400)

    def form_invalid(self, form):
        return JsonResponse({"error": "❌ برجاء إدخال بريد إلكتروني صحيح."}, status=400)