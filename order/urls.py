from django.urls import path
from .views import place_order, payment
urlpatterns = [
    path('payment/',payment, name="payment"),
    path('place-order/', place_order,name='place_order' ),
    
]