from typing import cast
from django.contrib import admin
from django.db import models
from .models import Product, ProductGallery, Variation, ReviewRating
import admin_thumbnails
# Register your models here.
@admin_thumbnails.thumbnail('image')

class ProductGalleryInLine(admin.TabularInline):
    model=ProductGallery
    extra=1

class ProductAdmin(admin.ModelAdmin):
    list_display=('product_name','price','stock','category','created_date','modified_date','is_available')
    prepopulated_fields={'slug':('product_name',)}
    inlines=[ProductGalleryInLine]

class VariationAdmin(admin.ModelAdmin):
    list_display=('product','variation_category','variation_value','is_active','created_date')
    list_filter=('product','variation_category','variation_value')
    list_editable=('is_active',)

admin.site.register(Product,ProductAdmin)
admin.site.register(Variation,VariationAdmin)
admin.site.register(ReviewRating)
admin.site.register(ProductGallery)