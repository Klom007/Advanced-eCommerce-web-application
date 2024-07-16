from django.db import models
from Mystore.models import products, variation
from Accounts.models import theaccount

# Create your models here.

class Thecart(models.Model):
    cart_id = models.CharField(max_length=250, blank=True)
    date_added= models.DateField(auto_now_add=True)

    def __str__(self):
        return self.cart_id


class cartItem(models.Model):
    theuser = models.ForeignKey(theaccount, on_delete=models.CASCADE, null=True)
    cart_product = models.ForeignKey(products, on_delete=models.CASCADE)
    variations = models.ManyToManyField(variation, blank=True)
    thecart = models.ForeignKey(Thecart, on_delete=models.CASCADE, null=True)
    quantity = models.IntegerField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.cart_product} - {self.quantity}"
    
    def sub_total(self):
        return self.cart_product.price * self.quantity