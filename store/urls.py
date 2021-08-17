from django.urls import path
from .views import store, product_details
urlpatterns = [
    path('store/', store,name='store' ),
    path('store/<slug:category_slug>/', store,name='store_category' ),
    path('store/<slug:category_slug>/<slug:product_slug>/', product_details,name='product_details' ),
]