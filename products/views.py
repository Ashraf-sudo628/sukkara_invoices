
from pyexpat.errors import messages
from django.shortcuts import get_object_or_404, render, redirect
from .models import *
from .forms import *
from django.contrib.auth.decorators import login_required
# Create your views here.

@login_required
def add_product(request):
    if request.method == "POST":
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save(commit=False)
            product.supplier = request.user.supplier  # يربط المنتج بالمورد المسجل حاليًا
            product.save()
            return redirect('product-list-supplier')  # تغييرها حسب الصفحة التي تريد إعادة التوجيه إليها
    else:
        form = ProductForm()
    
    return render(request, "products/add_product.html", {"form": form})

@login_required
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id, supplier=request.user.supplier)  # ضمان أن المورد يعدل منتجاته فقط

    if request.method == "POST":
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect('product-list-supplier')  # توجيه المستخدم إلى قائمة المنتجات بعد التعديل
    else:
        form = ProductForm(instance=product)

    return render(request, "products/edit_product.html", {"form": form, "product": product})

@login_required
def delete_product(request,product_id):
    product = get_object_or_404(Product, id=product_id)
    product.delete()
    return redirect('product-list-supplier')

@login_required
def product_list_supplier(request):
    try:
        supplier = request.user.supplier  # جلب كائن المورد المرتبط بالمستخدم
        products = Product.objects.filter(supplier=supplier)
    except AttributeError:
        messages.error(request, "أنت لست موردًا!")
        return redirect('dashboard')  # إعادة توجيه غير الموردين
    context = {'products': products}
    return render(request, 'products/product_list_supplier.html', context)

def product_list(request):
    if request.user.is_staff:
        products = Product.objects.all()
    else:
        try:
            supplier = request.user.supplier  # جلب المورد المرتبط بالمستخدم
            products = Product.objects.filter(supplier=supplier)  # عرض فواتيره فقط
        except AttributeError:
            print("no products")  # إذا لم يكن المورد مسجلاً، لا تعرض أي فواتير
    print()
    context = {'products': products}
    return render(request, 'products/products_list.html', context)