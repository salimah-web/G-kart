from django.urls import path
from .views import place_order, payment,order_complete
urlpatterns = [
    path('payment/',payment, name="payment"),
    path('order_complete/',order_complete, name="order_complete"),
    path('place-order/', place_order,name='place_order' ),
    
]