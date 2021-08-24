from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404, redirect, render
from .models import Cart, Cart_item
from store.models import Product
# Create your views here.
def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart

def add_to_cart(request, product_id):
    product=Product.objects.get(id=product_id)

    try:
        cart=Cart.objects.get(cart_id=_cart_id(request))
    except Cart.DoesNotExist:
        cart= Cart.objects.create(cart_id=_cart_id(request))
    cart.save()

    try:
        cart_item=Cart_item.objects.get(product=product, cart= cart)
        cart_item.quantity+=1
        cart_item.save()
    except Cart_item.DoesNotExist:
        cart_item=Cart_item.objects.create(product=product,cart=cart,quantity=1)
        cart_item.save()

    return redirect('cart')

def remove_cart_item(request, product_id):
    product=get_object_or_404(Product, id=product_id)
    cart=Cart.objects.get(cart_id=_cart_id(request))
    cart_item=Cart_item.objects.get(product=product, cart=cart)
    cart_item.delete()
    return redirect('cart')

def remove_cart(request,product_id):
    product=get_object_or_404(Product, id=product_id)
    cart=Cart.objects.get(cart_id=_cart_id(request))
    cart_item=Cart_item.objects.get(product=product, cart=cart)
    if cart_item.quantity>1:
        cart_item.quantity-=1
        cart_item.save()
    else:
        cart_item.delete()
    return redirect('cart')
def cart(request, total=0, quantity=0, cart_items=None):
    cart=Cart.objects.get(cart_id=_cart_id(request))
    cart_items=Cart_item.objects.filter(cart=cart, is_active=True)
    try:
        for cart_item in cart_items:

            total+=cart_item.product.price*cart_item.quantity
            quantity+=cart_item.quantity
        tax=2*total/100
        grand_total=tax+total
    except ObjectDoesNotExist:
        pass
    context={
        'total':total,
        'quantity':quantity,
        'cart_items':cart_items,
        'grand_total':grand_total,
        'tax':tax
    }
    return render(request, 'cart.html', context)