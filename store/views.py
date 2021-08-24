from django.core import paginator
from category.models import Category
from django.shortcuts import render, get_object_or_404
from .models import Product
from category.models import Category
from cart.models import Cart_item
from cart.views import _cart_id
from django.db.models import Q
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
    context={
        'single_product':single_product,
        'in_cart':in_cart

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