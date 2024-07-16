from .models import cartItem, Thecart
from .views import _cart_id_session

def cartcounter(request):
    cart_count = 0
    if 'admin' in request.path:
        return {}
    else:
        try:
            cart = Thecart.objects.filter(cart_id=_cart_id_session(request))
            if request.user.is_authenticated:
                cart_items = cartItem.objects.all().filter(theuser= request.user)
            else:

                cart_items = cartItem.objects.all().filter(thecart = cart[:1])
            for i in cart_items:
                cart_count += i.quantity
        except Thecart.DoesNotExist:
            cart_count = 0
    return dict(cart_count = cart_count)