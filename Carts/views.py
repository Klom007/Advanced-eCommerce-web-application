from django.shortcuts import render, redirect, get_object_or_404
from Mystore.models import products
from .models import Thecart, cartItem
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from Mystore.models import variation
from django.contrib.auth.decorators import login_required



# Create your views here.

def _cart_id_session(request):  #_ makes it a private function
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart

def add_cart(request, product_id):
    current_user = request.user
    Product = products.objects.get(id= product_id) # get the product
    #check if user is authenticated
    if current_user.is_authenticated:

        product_variation = []
        if request.method == 'POST':
                
            for item in request.POST:
                key = item
                value = request.POST[key]
            
                try:
                    Variation = variation.objects.get(product = Product, variation_category__iexact=key, variation_value__iexact=value)
                    product_variation.append(Variation)
                except:
                    pass
        
    
        
        
        is_cart_item_exists = cartItem.objects.filter(cart_product = Product, theuser=current_user).exists()


        if is_cart_item_exists:
            cart_item = cartItem.objects.filter(cart_product = Product, theuser=current_user)
         
            ex_var_list = []
            id = []
            for item in cart_item:
                existingvariation = item.variations.all()
                ex_var_list.append(list(existingvariation))
                id.append(item.id)
           

            if product_variation in ex_var_list:
                #increase the cart item qty
                index = ex_var_list.index(product_variation)
                item_id = id[index]
                item = cartItem.objects.get(cart_product = Product, id = item_id) #heherere
                item.quantity +=1
                item.save()

            else:
                item = cartItem.objects.create(cart_product = Product, quantity=1, theuser=current_user)
                if len(product_variation) > 0:
                    item.variations.clear()
                    
                    item.variations.add(*product_variation)
            
                item.save()
        else:
            cart_item = cartItem.objects.create(
                cart_product = Product,
                quantity = 1,
                theuser=current_user,

            )
            if len(product_variation) > 0:
                cart_item.variations.clear()
            
                cart_item.variations.add(*product_variation)  
            cart_item.save()
        
        return redirect('cart')




#if the user is not authenticated

        

    else:
        
        product_variation = []
        if request.method == 'POST':
                
            for item in request.POST:
                key = item
                value = request.POST[key]
            
                try:
                    Variation = variation.objects.get(product = Product, variation_category__iexact=key, variation_value__iexact=value)
                    product_variation.append(Variation)
                except:
                    pass
        
    
        
        try:
            cart = Thecart.objects.get(cart_id=_cart_id_session(request)) #get the cart using the cart_id present in the session
        except Thecart.DoesNotExist:
            cart = Thecart.objects.create(
                cart_id = _cart_id_session(request)
            )
        cart.save()

        is_cart_item_exists = cartItem.objects.filter(cart_product = Product, thecart=cart).exists()


        if is_cart_item_exists:
            cart_item = cartItem.objects.filter(cart_product = Product, thecart = cart)
            #existing variations 
            #current variation

            ex_var_list = []
            id = []
            for item in cart_item:
                existingvariation = item.variations.all()
                ex_var_list.append(list(existingvariation))
                id.append(item.id)
            print(ex_var_list)

            if product_variation in ex_var_list:
                #increase the cart item qty
                index = ex_var_list.index(product_variation)
                item_id = id[index]
                item = cartItem.objects.get(cart_product = Product, id = item_id) #heherere
                item.quantity +=1
                item.save()

            else:
                item = cartItem.objects.create(cart_product = Product, quantity=1, thecart=cart)
                if len(product_variation) > 0:
                    item.variations.clear()
                    
                    item.variations.add(*product_variation)
            
                item.save()
        else:
            cart_item = cartItem.objects.create(
                cart_product = Product,
                quantity = 1,
                thecart = cart,

            )
            if len(product_variation) > 0:
                cart_item.variations.clear()
            
                cart_item.variations.add(*product_variation)  
            cart_item.save()
        
        return redirect('cart')

def reduce_cart(request, product_id, cart_item_id):
    
    theproduct = get_object_or_404(products, id= product_id)
    try:
        if request.user.is_authenticated:
            thecartItem = cartItem.objects.get(cart_product = theproduct, theuser=request.user, id =cart_item_id )
        else:
            cart = Thecart.objects.get(cart_id = _cart_id_session(request))

            thecartItem = cartItem.objects.get(cart_product = theproduct, thecart=cart, id =cart_item_id )
        if thecartItem.quantity > 1:
            thecartItem.quantity -= 1

            thecartItem.save()
        else:
            thecartItem.delete()
    except:
        pass
    return redirect('cart')

def delete_cart(request, product_id, cart_item_id):
   
    theproduct = get_object_or_404(products, id= product_id)
    if request.user.is_authenticated:
         thecartItem = cartItem.objects.get(cart_product = theproduct, theuser=request.user, id = cart_item_id )
    else:
        cart = Thecart.objects.get(cart_id = _cart_id_session(request))
        thecartItem = cartItem.objects.get(cart_product = theproduct, thecart=cart, id = cart_item_id )
    thecartItem.delete()
    return redirect('cart')




def cart(request, total = 0, quantity = 0, cart_items = None):
    try:
        tax = 0
        grand_total = 0
        if request.user.is_authenticated:
            cart_items = cartItem.objects.filter(theuser= request.user, is_active=True)
        else:
            cart = Thecart.objects.get(cart_id = _cart_id_session(request))
            cart_items = cartItem.objects.filter(thecart = cart, is_active = True)
        for i in cart_items:
            total += (i.cart_product.price * i.quantity)
            quantity += i.quantity
        
        tax = (2 * total / 100)
        grand_total = total + tax

    except ObjectDoesNotExist:
        pass

    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'grand_total': grand_total,


    }



    return render(request, 'Carts/cart.html', context)


@login_required(login_url='login')
def checkout(request, total = 0, quantity = 0, cart_items = None):
    try:
        tax = 0
        grand_total = 0
        
        if request.user.is_authenticated:
            cart_items = cartItem.objects.filter(theuser= request.user, is_active=True)
        else:
            cart = Thecart.objects.get(cart_id = _cart_id_session(request))
            cart_items = cartItem.objects.filter(thecart = cart, is_active = True)
            
        for i in cart_items:
            total += (i.cart_product.price * i.quantity)
            quantity += i.quantity
        
        tax = (2 * total / 100)
        grand_total = total + tax

    except ObjectDoesNotExist:
        pass

    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'grand_total': grand_total,


    }


    return render(request, 'Carts/checkout.html', context)