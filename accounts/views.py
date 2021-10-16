from decimal import Context
from django import contrib
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404, redirect, render
from .forms import RegistrationForm, UserForm, UserProfileForm
from .models import Account, UserProfile
from django.contrib import messages,auth
from django.contrib.auth.decorators import login_required
# Create your views here.
from urllib.parse import ParseResult, urlparse
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode,urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from cart.models import Cart,Cart_item
from cart.views import _cart_id
import requests

from order.models import Order, OrderProduct, Payment
from cart.models import Cart_item
def register(request):
    if request.POST:
        form=RegistrationForm(request.POST)
        if form.is_valid():
            first_name=form.cleaned_data['first_name']
            last_name=form.cleaned_data['last_name']
            email=form.cleaned_data['email']
            phone_number=form.cleaned_data['phone_number']
            password=form.cleaned_data['password']
            username=email.split('@')[0]
            user= Account.objects.create_user(first_name=first_name,last_name=last_name,email=email,password=password,username=username)
            user.phone_number=phone_number
            user.save()

            UserProfile.objects.create(user=user)

            current_site=get_current_site(request)
            mail_subject="Please activate your mail"
            message=render_to_string('verify_email.html',{
                'user':user,
                'domain':current_site,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                'token':default_token_generator.make_token(user)
            }
            )
            to_email=email
            send_email=EmailMessage(mail_subject,message,to=[to_email])
            send_email.send()
            return redirect('/account/signin/?command=verification&email='+email)

    else:
        form = RegistrationForm()
    context={
        'form':form
    }
    return render(request,'register.html',context)

def sign_in(request):
    if request.method=="POST":
        email=request.POST['email']
        password=request.POST['password']
        user = auth.authenticate(email=email,password=password)
        if user is not None:
            try:
                cart=Cart.objects.get(cart_id=_cart_id(request))
                cart_item_exist=Cart_item.objects.filter( cart=cart).exists()
                if cart_item_exist:
                    cart_item=Cart_item.objects.filter(cart=cart)
                    pro_var=[]
                    for item in cart_item:
                       var=item.variation.all()
                       pro_var.append(list(var))

                    cart_items=Cart_item.objects.filter(user=user)
                    exs_var=[]
                    item_id=[]
                    for cart_item in cart_items:
                        var=cart_item.variation.all()
                        id=cart_item.id
                        exs_var.append(list(var))
                        item_id.append(id)
                               
                    for pr in pro_var:
                        if pr in exs_var:
                            index=exs_var.index(pr)
                            id=item_id[index]
                            item=Cart_item.objects.get(id=id)
                            item.quantity+=1
                            item.user=user
                            item.save()
                        else:
                            item.user=user
                            print(item.user)
                            item.save()
                            print(item.user)
            except:    
                pass
            auth.login(request, user)
            url8=request.META.get("HTTP_REFERER")
            try:
                query=requests.utils.urlparse(url8).query
                param=dict(x.split("=") for x in query.split('&'))
                print(param)
                if "next" in param:
                    nextpage=param["next"]
                    return redirect (nextpage)
            except:
                return redirect('dashboard')               
        else:
            messages.error(request, 'Invalid credentials')
            return redirect("signin")
    return render(request,'signin.html')
@login_required(login_url="signin")
def logout(request):
    auth.logout(request)
    messages.success(request, "You have logged out succesfully")
    return redirect("signin")

def activate_email(request,uidb64,token):
    try:
        uid=urlsafe_base64_decode(uidb64).decode()
        user=Account._default_manager.get(pk=uid)
    except (TypeError, ValueError,OverflowError, Account.DoesNotExist):
        user=None
    if user!= None and default_token_generator.check_token(user, token):
        user.is_active=True
        user.save()
        messages.success(request, "Your account has been verified.")
        return redirect('signin')
    else:
        messages.error(request, "Invalid token")
        return redirect('register')

@login_required(login_url="signin")
def dashboard(request):
    user=request.user
    orders=Order.objects.order_by('-created_at').filter(user_id=user.id, is_ordered=True)  
    orders_count=orders.count()
    try:
        userprofile=UserProfile.objects.get(user_id=user.id)
       
    except ObjectDoesNotExist:
        userprofile=None
    context={
        'orders_count':orders_count,
        'userprofile':userprofile
    }

    return render(request,'dashboard.html', context)    
@login_required(login_url="signin")
def my_orders(request):
    user=request.user
    orders=Order.objects.filter(user=user, is_ordered=True).order_by("-created_at")

    context={
        'orders':orders
               
    }

    return render(request,'My_orders.html', context)  
  


def forgot_password(request):
    if request.POST:
        email=request.POST['email']
        if Account.objects.filter(email=email).exists():
            user=Account.objects.get(email=email)
            current_site=get_current_site(request)
            mail_subject="Reset your password"
            message=render_to_string('reset_password.html',{
                'user':user,
                'domain':current_site,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                'token':default_token_generator.make_token(user)
            }
            )
            to_email=email
            send_email=EmailMessage(mail_subject,message,to=[to_email])
            send_email.send()
            messages.success(request, "Check you mail")
            return redirect('signin') 
        else:
            messages.error(request, "Account does not exist.")
            return redirect('forgot_password')
    return render(request, 'forgot_password.html')

def reset_password_validate(request, uidb64, token):
    try:
        uid=urlsafe_base64_decode(uidb64).decode()
        user=Account._default_manager.get(pk=uid)
    except (TypeError, ValueError,OverflowError, Account.DoesNotExist):
        user=None
    if user!= None and default_token_generator.check_token(user, token):
        request.session['uid']=uid
        messages.success(request, "Please reset your password")
        return redirect('reset_password')
    else:
        messages.error(request, "Link has expired")
        return redirect('signin')
        
def reset_password(request):
    if request.POST:
        password=request.POST['password']
        password1=request.POST['confirm_password']
        if password==password1:
            uid=request.session.get('uid')
            user=Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request, 'Password reset sucessful')
            return redirect('signin')
        else:
            messages.error(request, 'Passwords dont match!!')
            return redirect('reset_password')
    else:        
        return render(request, 'set_password.html')
@login_required(login_url="signin")
def EditProfile(request):  
    userprofile=get_object_or_404(UserProfile, user=request.user)
    if request.method == "POST":
        user_form=UserForm(request.POST, instance=request.user)
        userprofile_form=UserProfileForm(request.POST, request.FILES, instance =userprofile)
        if user_form.is_valid() and userprofile_form.is_valid():
            user_form.save()
            userprofile_form.save()
            messages.success(request, 'Your profile has been updated')
            return redirect('edit_profile')
    else:
        user_form=UserForm(instance=request.user)
        userprofile_form=UserProfileForm(instance =userprofile)
    context={
        'userprofile_form':userprofile_form,
        'user_form':user_form ,
        'userprofile':userprofile     
    }
    return render(request, 'edit_profile.html', context)
@login_required(login_url="signin")
def change_password(request):
    if request.method=="POST":
        current_passowrd=request.POST['current_password']
        new_password=request.POST['password_1']
        confirm_password=request.POST['password_2']

        user= Account.objects.get(username__exact=request.user.username)

        if new_password==confirm_password:
            success=user.check_password(current_passowrd)
            if success:
                user.set_password(new_password)
                user.save()

                messages.success(request, 'Password updated succesfully.')
                return redirect("change_password")
            else:
                messages.error(request, "Please enter a valid current password")
                return redirect ('change_password')
        else:
            messages.error(request, "Passwords does not match")
            return redirect('change_password')

    return render(request, 'change_password.html')
@login_required(login_url="signin")
def order_detail(request, order_id):   
    try:
        order=Order.objects.get(order_number=order_id)
        ordered_products=OrderProduct.objects.filter(order_id=order.id)
        
        subtotal=0
        for i in ordered_products:
            subtotal+=i.product_price*i.quantity

        #payment=Payment.objects.get(payment_id=transID)

        context={
            'order':order,
            'ordered_products':ordered_products,
            'order_number':order.order_number,
            'subtotal':subtotal
            
        }
        return render(request, 'order_details.html', context)
    except (Order.DoesNotExist, Payment.DoesNotExist):
        return redirect('my_orders')