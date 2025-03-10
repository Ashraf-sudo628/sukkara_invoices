from django import forms # type: ignore
from .models import *
from orders.models import *
from datetime import date 
from django.db.models import F, ExpressionWrapper, DurationField

class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ['paid_amount']

class InvoiceItemForm(forms.ModelForm):
    class Meta:
        model = InvoiceItem
        fields = ['product_name', 'quantity', 'unit_price','expired_quantity']
        
class PaymentForm(forms.ModelForm):
    class Meta:
        model = InvoicePayment
        fields = ['amount']
        labels = {'amount': 'المبلغ المدفوع'}
        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'أدخل المبلغ'}),
        }
        
# نموذج المنتجات الأصلية (غير قابل للتعديل)
class InvoiceItemFormReadOnly(forms.ModelForm):
    class Meta:
        model = InvoiceItem
        fields = ('product_name', 'quantity', 'unit_price', 'total_price')
    
    def __init__(self, *args, **kwargs):
        super(InvoiceItemFormReadOnly, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['readonly'] = True
            
class ExpiredProductForm(forms.ModelForm):
    product_name = forms.ModelChoiceField(
        queryset=Product.objects.all(),
        empty_label="اختر المنتج"
    )
    class Meta:
        model = InvoiceItem
        fields = ['product_name', 'expired_quantity', 'image']
        labels = {
                'product_name': 'إسم المنتج',
                'expired_quantity': 'الكميه المُرتجعه',
                'image': 'صورة المُرتجع',
            }
    def __init__(self, *args, **kwargs):
        invoice = kwargs.pop('invoice', None)
        super().__init__(*args, **kwargs)
        if invoice:
            self.fields['product_name'].queryset = Product.objects.filter(supplier=invoice.supplier)
        self.fields['product_name'].widget.attrs.update({'class': 'form-select'})
        self.fields['image'].widget.attrs.update({'class': 'form-control'})
        self.fields['expired_quantity'].widget.attrs.update({'class': 'form-control'})