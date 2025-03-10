from django.urls import path # type: ignore
from . import views  # type: ignore
from django.contrib.auth import views as auth_views # type: ignore
from .views import *

urlpatterns = [
    path('', views.dashboard_redirect, name='home'),
    path('register/', views.supplier_registration, name='register'),
    path('', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('login/', CustomLoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('dashboard/', views.supplier_dashboard, name='dashboard'),
    path('edit-profile/', views.supplier_edit_profile, name='edit_supplier_profile'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('supplier/supplier-list/', views.supplier_list, name='supplier-list'),  
    path('supplier/<int:supplier_id>/', views.supplier_detail, name='supplier_detail'),
    path('supplier/<int:supplier_id>/create-order/', views.create_order_for_supplier, name='create_order'),
    # path('reset_password/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('reset_password/', CustomPasswordResetView.as_view(), name='password_reset'),
    path('reset_password_done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]

