from django import contrib
from django.shortcuts import redirect, render
from .forms import RegistrationForm
from .models import Account
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
            url=request.path
            print(url)
            try:
                q=urlparse(url)
                query=requests.utils.urlparse(url8).query
                print(query)
                print(q.path)
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
    return render(request,'dashboard.html')    

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

