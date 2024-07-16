from django.contrib import admin
from .models import Thecart, cartItem

# Register your models here.

class thecartAdmin(admin.ModelAdmin):
    list_display = ('cart_id', 'date_added')



class tcartItemAdmin(admin.ModelAdmin):
    list_display = ('cart_product', 'thecart', 'is_active')


admin.site.register(Thecart, thecartAdmin)
admin.site.register(cartItem, tcartItemAdmin)
