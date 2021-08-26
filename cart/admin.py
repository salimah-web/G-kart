from django.contrib import admin
from .models import Cart, Cart_item
# Register your models here.

class CartItemManager(admin.ModelAdmin):
    list_display=('product','cart','quantity','is_active')
    list_filter=('product',)

class CartManager(admin.ModelAdmin):
    list_display=('cart_id','date_added')
    

admin.site.register(Cart_item,CartItemManager)
admin.site.register(Cart,CartManager)