from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from Carts.models import cartItem
from .forms import OrderForm
import datetime
from .models import Order
import json
from .models import Payment
from .models import OrderProduct
from Mystore.models import products
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

# Create your views here.
def Orders(request):
    return HttpResponse('Hi')


def place_orders(request, total = 0, quantity = 0):
    current_user = request.user

    #if cart count is less than or equal to 0 then redirect to store
    cart_items = cartItem.objects.filter(theuser= current_user)
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('store')
    
    grand_total = 0
    tax = 0
    for cart_item in cart_items:
         total += (cart_item.cart_product.price * cart_item.quantity)
         quantity += cart_item.quantity
    
    tax = (2 * total / 100)
    grand_total = total + tax
        

    if request.method == 'POST':
        form = OrderForm(request.POST)

        if form.is_valid():

            data = Order()
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.phone = form.cleaned_data['phone']
            data.email = form.cleaned_data['email']
            data.address_line_1 = form.cleaned_data['address_line_1']
            data.address_line_2 = form.cleaned_data['address_line_2']
            data.country = form.cleaned_data['country']
            data.state = form.cleaned_data['state']
            data.city = form.cleaned_data['city']
            data.order_note = form.cleaned_data['order_note']
           

            data.order_total= grand_total
            data.tax = tax

            data.ip = request.META.get('REMOTE_ADDR')# TO get the user IP
            data.user = current_user 
            data.save()

            #generate order number

            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d = datetime.date(yr,mt,dt)
            current_date = d.strftime("%Y%m%d")

            order_number = current_date + str(data.id) #we got the data id bcos we already saved the data
            data.order_number = order_number
            data.save()

            theorder = Order.objects.get(user = current_user, is_ordered = False, order_number = order_number)

            context = {
                'theorder': theorder,
                'cart_items': cart_items,
                'total': total,
                'tax': tax,
                'grand_total': grand_total,

            }

            return render(request, 'Orders/payments.html', context)
    else:
        return redirect('checkout')
    



def payments(request): 
    body = json.loads(request.body) # this is coming from the paypal js script below the payment.html
    order = Order.objects.get(user = request.user, is_ordered= False, order_number = body['orderID'] )


    #store transaction details inside payment model 
    payment = Payment(user = request.user, 
                      payment_id = body['transID'],
                      payment_method = body['payment_method'],
                      amount_paid = order.order_total,
                      status = body['status'],
    )

    payment.save()
    order.payment = payment
    order.is_ordered = True
    order.save()

    print(body)
    #move the cart items to ordered product table
    cart_items = cartItem.objects.filter(theuser = request.user)
    for item in cart_items:
        orderproduct = OrderProduct()
        orderproduct.order_id = order.id  #_id to access the foreign key
        orderproduct.payment= payment
        orderproduct.user_id = request.user.id
        orderproduct.product_id = item.cart_product_id # you can use both . or _ to access the id
        orderproduct.quantity = item.quantity
        orderproduct.product_price = item.cart_product.price
        orderproduct.ordered = True
        orderproduct.save()

        cart_item = cartItem.objects.get(id = item.id)
        product_variation = cart_item.variations.all()
        orderproduct = OrderProduct.objects.get(id=orderproduct.id)
        orderproduct.variations.set(product_variation)
        orderproduct.save()


    #reduce the quantity of the sold product
        product = products.objects.get(id=item.cart_product_id)
        product.stock -= item.quantity
        product.save()


    #clear the cart
    cartItem.objects.filter(theuser = request.user).delete()


    #send order received email to customer
   
    mail_subject = 'Thank you for your order'
    message = render_to_string('Orders/order_received_email.html',{
         'user': request.user,
         'order': order,
         
    })
    to_email = request.user.email
    send_email = EmailMessage(mail_subject, message, to=[to_email])
    send_email.send()
           
    #send order number and transaction id back to SendData method via json response
    data = {
        'order_number': order.order_number,
        'transID': payment.payment_id,
    }
    return JsonResponse(data) #this line would send back the data to the javascript paypal method in
#payment.html
 

def Order_complete(request):
    order_number = request.GET.get('order_number') # after payment function executes it loads the Order_complete url and sends order_number and transID to the javasctipt which sends it to the url that is why we use get methord to check for them and fetch them
    transID = request.GET.get('payment_id')
    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        ordered_products = OrderProduct.objects.filter(order_id=order.id)
        payment = Payment.objects.get(payment_id = transID)
        subtotal = 0

        for i in ordered_products:
            subtotal += i.product_price * i.quantity

        context = {
            'order': order,
            'ordered_products': ordered_products,
            'order_number': order.order_number,
            'transID': payment.payment_id,
            'subtotal': subtotal,
            'payment': payment,
            #'transID': transID,   we can also do it this way then skip writting in the above payment = Payment.objects.get(payment_id = transID)
        }
        return render(request, 'Orders/Order_complete.html', context)
    except (Payment.DoesNotExist, Order.DoesNotExist):
        return redirect('home')











            
            
