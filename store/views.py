from django.core import paginator
# from django.core.checks import messages
from django.contrib import messages
from category.models import Category
from django.shortcuts import redirect, render, get_object_or_404
from .models import Product, ReviewRating, ProductGallery
from category.models import Category
from cart.models import Cart_item
from .forms import ReviewForm
from cart.views import _cart_id
from django.db.models import Q
from order.models import OrderProduct
from django.core.paginator import Paginator
# Create your views here.
def store(request,category_slug=None):
    categories=None
    products=None
    if category_slug!=None:
        categories=get_object_or_404(Category, slug=category_slug)
        products=Product.objects.all().filter(category=categories, is_available=True)
        paginator=Paginator(products,2)
        page=request.GET.get('page')
        paged_products=paginator.get_page(page)
        product_count=products.count()
    else:   
        products = Product.objects.all().filter(is_available=True)
        product_count=products.count()
        paginator=Paginator(products,2)
        page=request.GET.get('page')
        paged_products=paginator.get_page(page)
    context={
        'products':paged_products,
        'product_count':product_count
    }
    return render(request, 'store.html', context)

def product_details(request,category_slug=None,product_slug =None):
    try:
        single_product=Product.objects.get(category__slug=category_slug, slug = product_slug)
        in_cart=Cart_item.objects.filter(cart__cart_id=_cart_id(request),product=single_product).exists()
    except Exception as e:
        raise e

    if request.user.is_authenticated:
        try:    
            orderproduct=OrderProduct.objects.filter(user=request.user, product_id=single_product.id).exists()
        except OrderProduct.DoesNotExist:
            orderproduct=None
    else: 
        orderproduct=None
    reviews=ReviewRating.objects.filter(product_id=single_product.id, status=True)
    product_gallery=ProductGallery.objects.filter(product_id=single_product.id)
    context={
        'single_product':single_product,
        'in_cart':in_cart,
        'orderproduct':orderproduct,
        'reviews':reviews,
        'product_gallery':product_gallery
    }
    return render(request, "product-detail.html", context)

def search(request):
    if 'keyword' in request.GET:
        keyword=request.GET['keyword']
        if keyword:
            products=Product.objects.order_by('-created_date').filter(Q(description__icontains=keyword) | Q(product_name__icontains=keyword))
            count=products.count()
    context={
        'products':products,
        'product_count':count
    }
    return render(request,'store.html',context)

def SubmitReview(request, product_id):
    url = request.META.get('HTTP_REFERER')
    if request.method=="POST":
        try: 
            reviews=ReviewRating.objects.get(user__id=request.user.id, product__id=product_id)
            form = ReviewForm(request.POST, instance=reviews)
            form.save()
            messages.success(request, 'Thank you! Your review has been updated')
            return redirect (url)
        except ReviewRating.DoesNotExist:
            form = ReviewForm(request.POST)
            if form.is_valid():
                data=ReviewRating.objects.create(
                    subject=form.cleaned_data['subject'],
                    rating=form.cleaned_data['rating'],
                    review=form.cleaned_data['review'],
                    ip=request.META.get('REMOTE_ADDR'),
                    product_id=product_id,
                    user_id=request.user.id
                )

                data.save()
                messages.success(request, 'Thank you! Your review has been submitted')
                return redirect(url)
