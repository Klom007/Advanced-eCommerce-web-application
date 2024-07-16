from django.db import models
from django.urls import reverse

# Create your models here.
class Productcategory(models.Model):
    category_name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)
    description = models.TextField(max_length=255, blank=True)
    cat_image = models.ImageField(upload_to='photos/categories', blank=True)

    class Meta:
        verbose_name = 'Product Category'
        verbose_name_plural = 'Product Categories'

    def get_url(self):
        return reverse('products_by_category', args=[self.slug]) #products_by_category is coming from Mystore url

    def __str__(self):
        return self.category_name



