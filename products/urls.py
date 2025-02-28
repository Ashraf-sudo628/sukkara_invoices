from django import views
from django.urls import path
from . import views 

urlpatterns = [
    path('add/',views.add_product , name='add-product'),
    path('product/edit/<int:product_id>/', views.edit_product, name='edit_product'),
    path('product/delete/<int:product_id>/', views.delete_product, name='delete_product'),
    path('product/product-list-supplier/', views.product_list_supplier, name='product-list-supplier'),
    path('product/product-list/', views.product_list, name='product-list'),
]
