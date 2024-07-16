from django.db import models
from Category.models import Productcategory
from django.urls import reverse
from Accounts.models import theaccount
from django.db.models import Avg, Count

# Create your models here.
class products(models.Model):
    product_name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True)
    product_description = models.TextField(max_length=500, blank=True)
    price = models.IntegerField()
    image = models.ImageField(upload_to='photos/products')
    stock = models.IntegerField()
    is_available = models.BooleanField(default=True)
    category = models.ForeignKey(Productcategory, on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = 'Products'

    
    def get_product_url(self):
        return reverse('product_detail', args=[self.category.slug, self.slug]) #product_detail is the name of the url path in Mystoreurls.py

      
    def averageReview(self):
        reviews = ReviewRating.objects.filter(product=self, status=True).aggregate(average=Avg('rating'))
        avg = 0
        if reviews['average'] is not None:
            avg = float(reviews['average'])
        return avg
    
    def countReview(self):
        reviews = ReviewRating.objects.filter(product=self, status=True).aggregate(count=Count('id'))
        count = 0
        if reviews['count'] is not None:
            count = int(reviews['count'])
        return count



    def __str__(self):
        return self.product_name



class variationManager(models.Manager):
    def colors(self):
        return super(variationManager, self).filter(variation_category='color', is_active=True)
    
    def sizes(self):
        return super(variationManager, self).filter(variation_category='size', is_active=True)



variation_category_choice = (
    ('color', 'color'),
    ('size', 'size'),
)


class variation(models.Model):
    product = models.ForeignKey(products, on_delete=models.CASCADE)
    variation_category = models.CharField(max_length=100, choices=variation_category_choice)
    variation_value = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now=True)

    objects = variationManager()


    def __str__(self):
        return self.variation_value

    
class ReviewRating(models.Model):
    product = models.ForeignKey(products, on_delete=models.CASCADE)
    user = models.ForeignKey(theaccount, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100, blank=True)
    review = models.TextField(max_length=500, blank=True)
    rating = models.FloatField()
    ip = models.CharField(max_length=20, blank=True)
    status = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.subject
    
class ProductGallery(models.Model):
    product = models.ForeignKey(products, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='store/product', max_length=255)

    def __str__(self):
        return self.product.product_name
    
    class Meta:
        verbose_name = 'Product Gallery'
        verbose_name_plural = 'Product Gallery'