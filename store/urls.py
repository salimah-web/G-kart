from django.urls import path
from .views import store, product_details,search, SubmitReview
urlpatterns = [
    path('store/', store,name='store' ),
    path('submit_review/<int:product_id>/', SubmitReview,name='submit_review' ),
    path('store/category/<slug:category_slug>/', store,name='store_category' ),
    path('store/category/<slug:category_slug>/<slug:product_slug>/', product_details,name='product_details' ),
    path('store/search', search,name='search' ),
]