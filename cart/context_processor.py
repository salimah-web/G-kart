from django.core.exceptions import ObjectDoesNotExist
from .views import _cart_id
from .models import Cart_item, Cart

def counter(request):
    if 'admin' in request.path:
        return {}
    else:
        try:
            count=0
            cart=Cart.objects.filter(cart_id=_cart_id(request))
            cart_items=Cart_item.objects.all().filter(cart=cart[:1])
            for cart_item in cart_items:
                count+=cart_item.quantity
        except ObjectDoesNotExist:
            count=0
        return dict(count=count) 
