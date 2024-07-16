

from django.contrib import admin
from django.urls import path
from . import views


urlpatterns = [

    path('', views.Orders, name='Orders'),
    
    path('place_orders/', views.place_orders, name='place_orders'),

    path('payments/', views.payments, name='payments'),

    path('Order_complete/', views.Order_complete, name='Order_complete'),


   
]



