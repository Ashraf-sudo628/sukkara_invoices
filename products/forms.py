from django import forms
from .models import *

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'purchase_price', 'selling_price', 'expiry_period', 'notes']
        labels = {
            'name': 'اسم المنتج',
            'purchase_price': 'سعر الشراء',
            'selling_price': 'سعر البيع (إختياري)',
            'expiry_period': 'مدة الصلاحية',
            'notes': 'ملاحظات',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control col-6' }),
            'purchase_price': forms.NumberInput(attrs={'class': 'form-control'}),
            'selling_price': forms.NumberInput(attrs={'class': 'form-control'}),
            'expiry_period': forms.NumberInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3 ,'placeholder':'الملاحظات حول طريقة التخزين أو في حال وجود ملاحظات أخرى بما يشمل سياسة الرجيع'}),
        }