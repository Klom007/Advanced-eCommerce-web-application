
from django.contrib import admin
from django.urls import path
from . import views


urlpatterns = [
    path('register/', views.register, name='register'),

    path('login/', views.login, name='login'),

    path('logout/', views.logout, name='logout'),

    path('activate/<uidb64>/<token>/', views.activate, name='activate'),

    path('regthank/', views.regthank, name='regthank'),

    path('dashboard/', views.dashboard, name='dashboard'),

    path('my_orders/', views.my_orders, name='my_orders'),

    path('order_detail/<int:order_id>/', views.order_detail, name='order_detail'),

    
    path('edit_profile/', views.edit_profile, name='edit_profile'),

    
    path('change_password/', views.change_password, name='change_password'),

    path('', views.dashboard, name='dashboard'),

    path('forgotPassword/', views.forgotPassword, name='forgotPassword'),

    path('reset_password_validate/<uidb64>/<token>/', views.reset_password_validate, name='reset_password_validate'),

    path('resetPassword/', views.resetPassword, name='resetPassword'),
    
  
]

