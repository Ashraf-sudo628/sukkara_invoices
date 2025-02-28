from django import forms # type: ignore
from django.contrib.auth.models import User # type: ignore
from .models import Supplier

class SupplierRegistrationForm(forms.ModelForm):
    username = forms.CharField(
        max_length=150,
        label="اسم المستخدم",
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    email = forms.EmailField(
        label="البريد الإلكتروني",
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
    )
    password = forms.CharField(
        label="كلمة المرور",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )
    confirm_password = forms.CharField(
        label="تأكيد كلمة المرور",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        
    def clean(self):
        cleaned_data      = super().clean()
        password          = cleaned_data.get('password')
        confirm_password  = cleaned_data.get('confirm_password')
        
        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "كلمتا المرور غير متطابقتين.")# type: ignore

class SupplierEditForm(forms.ModelForm):
    class Meta:
        model = Supplier  
        fields = ['company_name', 'email', 'bank_account', 'phone_number', 'address']
        labels = {
            'company_name': 'الأسم',
            'email': 'البريد الإلكتروني',
            'bank_account': 'رقم الحساب البنكي',
            'phone_number': 'رقم الهاتف',
            'address': 'العنوان'
        }
        widgets = {
            'company_name': forms.TextInput(attrs={'class': 'form-control' }),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'bank_account': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }