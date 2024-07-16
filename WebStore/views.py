from django.http import HttpResponse
from django.shortcuts import render
from Mystore.models import products
from Mystore.models import ReviewRating


def home(request):
    theproducts = products.objects.all().filter(is_available=True).order_by('-created_date')

    for thisproduct in theproducts:

        reviews = ReviewRating.objects.filter(product = thisproduct, status = True)



    context = {
        'theproducts': theproducts,
        'reviews': reviews, 
    }
    return render(request, 'home.html', context)
    #return HttpResponse('This is my home')