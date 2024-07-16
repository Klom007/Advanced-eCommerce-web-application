from django.contrib import admin
from .models import products, variation
from .models import ReviewRating
from .models import ProductGallery
import admin_thumbnails

@admin_thumbnails.thumbnail('image')
class productGalleryInline(admin.TabularInline): 
    model = ProductGallery
    extra = 1



class productAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'category', 'stock', 'modified_date', 'is_available' )
    prepopulated_fields = {'slug': ('product_name',)}
    inlines = [productGalleryInline]  #we made an inline using ProductGallery then passed it here so it would have the images


class variationAdmin(admin.ModelAdmin):
    list_display = ('product', 'variation_category', 'variation_value', 'is_active')
    list_editable = ('is_active',)
    list_filter = ('product', 'variation_category', 'variation_value')
    ordering = ('id',)


admin.site.register(products, productAdmin)

admin.site.register(variation, variationAdmin)

admin.site.register(ReviewRating)
admin.site.register(ProductGallery)