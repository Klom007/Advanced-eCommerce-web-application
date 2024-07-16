from django.shortcuts import render, get_object_or_404, redirect
from .models import products, ReviewRating
from Category.models import Productcategory
from Carts.models import cartItem
from Carts.views import _cart_id_session
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q
from django.http import HttpResponse
from .forms import ReviewForm
from django.contrib import messages
from Orders.models import OrderProduct
from django.db.models import Avg
from .models import ProductGallery


# Create your views here.


def store(request, category_slug=None):
    categories = None
    theproducts = None

    if category_slug != None:
        categories = get_object_or_404(Productcategory, slug =category_slug)
        theproducts = products.objects.filter(category=categories, is_available=True)
         #paginator code 
        thepagonator = Paginator(theproducts, 1)
        page = request.GET.get('page')
        paged_products = thepagonator.get_page(page)
        #paginator ends
        product_count = theproducts.count()
    else:
        theproducts = products.objects.all().filter(is_available=True).order_by('id')
        #paginator code 
        thepagonator = Paginator(theproducts, 3)
        page = request.GET.get('page')
        paged_products = thepagonator.get_page(page)
        #paginator ends
        product_count = theproducts.count()
    

    context = {
        'theproducts': paged_products,
        #'theproducts': theproducts, this was how it was before i added paginator
        'product_count': product_count,
    }

    return render(request, 'Mystore/store.html', context)


def product_detail(request, category_slug, product_slug):
    try:
        single_product = products.objects.get(category__slug=category_slug, slug = product_slug)
        in_cart = cartItem.objects.filter(thecart__cart_id=_cart_id_session(request), cart_product=single_product).exists()
       
    except Exception as e:
        raise e
    
    if request.user.is_authenticated:
        try: #checke if the logged in user has puchased this product so we can allow him make a review
            orderproduct = OrderProduct.objects.filter(user = request.user, product_id = single_product.id).exists()
        except OrderProduct.DoesNotExist:
            orderproduct = None
    else:
        orderproduct = None
    #get the views
    reviews = ReviewRating.objects.filter(product = single_product, status = True)

    # get the product galery
    product_galery = ProductGallery.objects.filter(product = single_product)

    
    context = {
        'single_product': single_product,
        'in_cart': in_cart,
        'orderproduct': orderproduct,
        'reviews': reviews,
        'product_galery': product_galery,
        
    }

    return render(request, 'Mystore/product_detail.html', context)


def search3(request):
    product = None
    product_count = 0

    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            product = products.objects.order_by('-created_date').filter(Q(product_description__icontains=keyword) | Q(product_name__icontains=keyword))
            product_count = product.count()
    context = {
        'product': product,
        'product_count': product_count,
    }
    return render(request, 'Mystore/store.html', context)


def search(request): #this search url is using same page as store url and they both use Mystore/store.html. therefore the search variable which is 
    #theproducts has to be the same in the both becouse the html was designed with theproducts. if you dont want it this way then create a seperate page for the search url and design it. they also use the same product_count variable
    keyword = request.GET.get('keyword')  # Get the search keyword from the request
    theproducts = None

    if keyword: 
        # Filter products where the product_name contains the keyword
        theproducts = products.objects.order_by('-created_date').filter(Q(product_description__icontains=keyword) | Q(product_name__icontains=keyword))
        product_count = theproducts.count()

    context = {
        'theproducts': theproducts,
        'keyword': keyword,  # Pass the keyword back to the template for display
        'product_count': product_count,
    }

    return render(request, 'Mystore/store.html', context)

   
    



#the search form methord is GET so it passsed what you typed and saves it in the name attrobute 
#which we called keyword so in the above code it checks first if the there is keyword in the url and 
#then passes the keyword into the searchterm variable


def submitReview(request, product_id):
    url = request.META.get('HTTP_REFERER') #storing the current url so we can redirect the user after they have submited a review
    if request.method =='POST':
        try:
            reviews = ReviewRating.objects.get(user=request.user, product_id=product_id) #user is a foreign key in the model thats why i used __to access the id
            form = ReviewForm(request.POST, instance=reviews)
            form.save()
            messages.success(request, 'Thank you, review has been updated')
            return redirect(url)


        except ReviewRating.DoesNotExist:
            form = ReviewForm(request.POST)
            if form.is_valid():
                data = ReviewRating()
                data.subject = form.cleaned_data['subject']
                data.rating = form.cleaned_data['rating']
                data.review = form.cleaned_data['review']
                data.ip = request.META.get('REMOTE_ADDR')
                data.product = products.objects.get(pk=product_id)  #this product_id is from the url
                data.user_id= request.user.id

                data.save()

                messages.success(request, 'Thank you, review has been submitted')
                return redirect(url)
            
