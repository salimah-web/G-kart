from order.models import Order
from django.shortcuts import redirect, render
from cart.models import Cart_item
from .forms import OrderForm
from .models import Order
import datetime
# Create your views here.
def payment(request):
    return render(request,'place-order.html')

def place_order(request, total=0,quantity=0 ):
    current_user=request.user
    print(current_user)
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
    print("hyu")
    if request.method == 'POST':
        form = OrderForm(request.POST)
        
        print("hi")
        if form.is_valid():
            data=Order.objects.create(
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