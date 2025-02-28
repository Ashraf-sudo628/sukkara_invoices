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
        queryset=Product.objects.none(),
        empty_label="اختر المنتج",
        widget=forms.Select(attrs={'class': 'form-control product-select'})
    )

    class Meta:
        model = InvoiceItem
        fields = ('product_name', 'expired_quantity', 'unit_price')
        widgets = {
                    'expired_quantity': forms.NumberInput(attrs={'class': 'form-control','required': 'false'})}
    def __init__(self, *args, **kwargs):
        supplier = kwargs.pop('supplier', None)
        super().__init__(*args, **kwargs)
        if supplier:
            today = date.today()
            self.fields['product_name'].queryset = OrderItem.objects.filter(
                order__supplier=supplier
            ).annotate(
                days_since_order=ExpressionWrapper(
                    today - F('order__order_date'),
                    output_field=DurationField()
                )
            ).filter(
                expiry_period__lt=F('days_since_order')
            ).distinct()