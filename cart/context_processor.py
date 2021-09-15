from django.core.exceptions import ObjectDoesNotExist
from .views import _cart_id
from .models import Cart_item, Cart

def counter(request):
    count=0
    if 'admin' in request.path:
        return {}
    else:
        try:           
            cart=Cart.objects.filter(cart_id=_cart_id(request))
            if request.user.is_authenticated:
                print(request.user.is_authenticated)
                cart_items=Cart_item.objects.all().filter(user=request.user)
                
            else:
                cart_items=Cart_item.objects.all().filter(cart=cart[:1])
            for cart_item in cart_items:
                count+=cart_item.quantity
        except ObjectDoesNotExist:
            count=0
        return dict(count=count) 
