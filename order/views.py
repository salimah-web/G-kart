from order.models import Order
from django.http import JsonResponse
from django.shortcuts import redirect, render
from cart.models import Cart_item
from .forms import OrderForm
from .models import Order, OrderProduct, Payment
import datetime
import json
from store.models import Product
from django.core.mail import EmailMessage, message, send_mail
from django.template.loader import render_to_string

# Create your views here.
def payment(request):
    body=json.loads(request.body)
    
    order=Order.objects.get(user=request.user, is_ordered=False, order_number=body['orderID'])

    payment=Payment(
        user=request.user,
        payment_id=body['transID'],
        payment_method=body['payment_method'],
        amount_paid=order.order_total,
        status=body['status']
    )
    payment.save()

    order.Payment=payment
    order.is_ordered= True
    order.save()

    #move the cart items to order product table
    cart_items=Cart_item.objects.filter(user=request.user)
    for item in cart_items:
        orderproduct=OrderProduct(
            order_id=order.id,
            payment=payment,
            user_id=request.user.id,
            product_id=item.product_id,
            quantity=item.quantity,
            product_price=item.product.price,
            ordered=True
        )
        
        orderproduct.save()
        cart_item=Cart_item.objects.get(id=item.id)
        product_variation=cart_item.variation.all()
        orderproduct=OrderProduct.objects.get(id=orderproduct.id)
        orderproduct.variation.set(product_variation)
        orderproduct.save()

        #Cant directly assign value to many_to many fields unless you save first

        #reduce quantity of the sold products
        product=Product.objects.get(id=item.product_id)
        product.stock-=item.quantity
        product.save()
    Cart_item.objects.filter(user=request.user).delete()    

    #send order receive email

    mail_subject='Thank you for your order!'
    message=render_to_string('order_received_email.html',{
        'user':request.user,
        'order':order
    })

    to_email=request.user.email
    send_mail=EmailMessage(mail_subject, message, to=[to_email])
    send_mail.send()

    data={
        "order_number":order.order_number,
        'transID':payment.payment_id
    }

    return JsonResponse(data)

def place_order(request, total=0,quantity=0 ):
    current_user=request.user
    cart_items=Cart_item.objects.filter(user=current_user)
    cart_count=cart_items.count()
    if cart_count<=0:
        return redirect("store")
    grand_total=0
    tax=0
    total=0
    for cart_item in cart_items:
        tot=(cart_item.product.price*cart_item.quantity)
        total+=tot
        quantity +=cart_item.quantity

    tax=(2*total)/100
    grand_total=total+tax
    
    if request.method == 'POST':
        form = OrderForm(request.POST)
        
        
        if form.is_valid():
            
            data=Order(
                user=current_user,          
                first_name=form.cleaned_data['first_name'],
                
                last_name=form.cleaned_data['last_name'],
                email=form.cleaned_data['email'],
                phone=form.cleaned_data['phone'],
                address=form.cleaned_data['address'],
                country=form.cleaned_data['country'],
                state=form.cleaned_data['state'],
                city=form.cleaned_data['city'],
                
                order_note=form.cleaned_data['order_note'],
                order_total=grand_total,
                tax=tax,
                ip=request.META.get('REMOTE_ADDR')
            )            
            data.save()
            print(data)
            yr=int(datetime.date.today().strftime("%Y"))
            dt=int(datetime.date.today().strftime("%d"))
            mt=int(datetime.date.today().strftime("%m"))
            d=datetime.date(yr,mt,dt)
            current_date=d.strftime("%Y%m%d")
            order_no=current_date+"-"+str(data.id)
            data.order_number=order_no
            data.save()
            order=Order.objects.get(user=current_user, is_ordered=False, order_number= order_no)
            context={
                'order':order,
                'total':total,
                'cart_items':cart_items,
                'grand_total':grand_total,
                'tax':tax
            }
            return render(request,'place-order.html', context)
    return redirect("checkout")

def order_complete(request):
    order_number=request.GET.get('order_number')
    transID=request.GET.get('payment_id')

    try:
        order=Order.objects.get(order_number=order_number)
        ordered_products=OrderProduct.objects.filter(order__id=order.id)
        
        subtotal=0
        for i in ordered_products:
            subtotal+=i.product_price*i.quantity

        payment=Payment.objects.get(payment_id=transID)

        context={
            'order':order,
            'ordered_product':ordered_products,
            'order_number':order.order_number,
            'transID':payment.payment_id,
            'payment':payment,
            'sub_total':subtotal
        }
        return render(request, 'order_complete.html', context)
    except (Payment.DoesNotExist, Order.DoesNotExist):
        return redirect('home')