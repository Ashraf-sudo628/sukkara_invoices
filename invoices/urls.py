from django.urls import path # type: ignore
from . import views  # type: ignore
from .tasks import *

urlpatterns = [
    path('create-invoice/<int:order_id>/', views.create_invoice_view, name='create_invoice'),
    path('invoice/<int:invoice_id>/', views.invoice_detail, name='invoice_detail'),
    path('invoices/add-payment/<int:invoice_id>/', views.add_payment, name='add_payment'),
    path('invoice/edit/<int:invoice_id>/', views.edit_daily_invoice, name='edit_daily_invoice'),
    path('invoice/invoice-list-supplier',views.invoice_list_supplier,name='invoice-list-supplier'),
    path('invoice/invoice-list',views.invoice_list,name='invoice-list')
    
    # path('update-invoice/<int:order_id>/', update_invoice, name='update_invoice'),
]