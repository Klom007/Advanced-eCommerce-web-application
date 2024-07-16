from django.contrib import admin
from .models import Productcategory
# Register your models here.


class productdategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('category_name',)}
    list_display = ('category_name', 'slug')

admin.site.register(Productcategory, productdategoryAdmin)
