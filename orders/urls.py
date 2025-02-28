from django.urls import path # type: ignore
from . import views  # type: ignore


urlpatterns = [
    path('create-order/', views.create_order, name='create_order'),
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),
    path('order/edit/<int:order_id>/', views.edit_order, name='edit_order'),
    path('order/delete/<int:order_id>/', views.delete_order, name='delete_order'),
    path('order/order-list-supplier/', views.order_list_supplier, name='order-list-supplier'),
    path('order/order-list/', views.order_list, name='order-list'),
    
]
