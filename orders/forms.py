from django import forms
from .models import * 

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['notes']
        widgets = {
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder':'الملاحظات حول طريقة التخزين أو في حال وجود ملاحظات أخرى بما يشمل سياسة الرجيع'})
        }
        
class OrderItemForm(forms.ModelForm):
    # product_name = forms.ModelChoiceField(
    #     queryset=Product.objects.all(),
    #     empty_label="اختر المنتج",
    #     widget=forms.Select(attrs={'class': 'form-control product-select'})
    # )
    product_name = forms.ModelChoiceField(
        queryset=Product.objects.all(),
        to_field_name="id",  # اجعل الفورم يتوقع الـ ID الخاص بالمنتج
        empty_label="اختر المنتج"
    )
    class Meta:
        model = OrderItem
        fields = ['id','product_name', 'quantity', 'price', 'expiry_period']
        widgets = {
            'expiry_period': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            
            
        }

    def __init__(self, *args, **kwargs):
        supplier = kwargs.pop('supplier', None)
        super().__init__(*args, **kwargs)
        if supplier:
            self.fields['name'].queryset = Product.objects.filter(supplier=supplier)
            
    def clean_quantity(self):
        quantity = self.cleaned_data.get("quantity")
        if quantity <= 0:
            raise forms.ValidationError("يجب أن تكون الكمية أكبر من 0.")
        return quantity
    
    def clean_product_name(self):
        product_name = self.cleaned_data.get("product_name")
        if isinstance(product_name, str):  # إذا كان النص مرسل بدل ID
            try:
                product = Product.objects.get(name=product_name)
                return product  # إرجاع الكائن بدلاً من النص
            except Product.DoesNotExist:
                raise forms.ValidationError("المنتج غير موجود!")
        return product_name