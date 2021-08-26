from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404, redirect, render
from .models import Cart, Cart_item
from store.models import Product,Variation
from django.http import HttpResponse
# Create your views here.
def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart

def add_to_cart(request, product_id):
    product=Product.objects.get(id=product_id)
    variations=[]
    if request.method=="POST":
        for item in request.POST:
            key=item
            value=request.POST[key]
            
            try:
                variation=Variation.objects.get(product=product, variation_category__iexact=key, variation_value__iexact=value)
                variations.append(variation)
            except:
                pass    

    try:
        cart=Cart.objects.get(cart_id=_cart_id(request))
    except Cart.DoesNotExist:
        cart= Cart.objects.create(cart_id=_cart_id(request))
    cart.save()

    
    cart_item_exist=Cart_item.objects.filter(product=product, cart=cart).exists()
    exist_var=[]
    id=[]
    if cart_item_exist:
        cart_item=Cart_item.objects.filter(product=product, cart= cart)

        for item in cart_item:
            #existing variation
            var=item.variation.all()
            exist_var.append(list(var))
            id.append(item.id)
            print(exist_var)
        if variations in exist_var:
            #currentvariation
            index=exist_var.index(variations)
            item_id=id[index]
            item=Cart_item.objects.get(product=product, id=item_id)
            item.quantity+=1
            item.save() 
        else:
            item=Cart_item.objects.create(product=product,cart=cart,quantity=1)
            if len(variations)>0:
                item.variation.clear()
                for i in variations:
                    print(item)
                    item.variation.add(i)

                    item.save()
    #cart_item.variation.clear()
    
    else:
        cart_item=Cart_item.objects.create(product=product,cart=cart,quantity=1)
        if len(variations)>0:
            cart_item.variation.clear()
            for item in variations:
                cart_item.variation.add(item)
        cart_item.save()

    return redirect('cart')

def remove_cart_item(request, product_id, cart_item_id):
    product=get_object_or_404(Product, id=product_id)
    cart=Cart.objects.get(cart_id=_cart_id(request))
    
    cart_item=Cart_item.objects.get(product=product, cart=cart, id=cart_item_id)
    cart_item.delete()
    return redirect('cart')

def remove_cart(request,product_id, cart_item_id):
    product=get_object_or_404(Product, id=product_id)
    try: 
        cart=Cart.objects.get(cart_id=_cart_id(request))
        cart_item=Cart_item.objects.get(product=product, cart=cart, id=cart_item_id)
        if cart_item.quantity>1:
            cart_item.quantity-=1
            cart_item.save()
        else:
            cart_item.delete()
    except:
        pass
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