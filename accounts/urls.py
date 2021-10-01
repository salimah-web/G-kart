from django.urls import path
from .views import order_detail, register, sign_in, logout, EditProfile, order_detail, change_password, my_orders, activate_email, dashboard,forgot_password,reset_password_validate,reset_password
urlpatterns = [
    path('register', register,name='register' ),
    path('signin/', sign_in,name='signin' ),
    path('forgot_password', forgot_password,name='forgot_password' ),
    path('reset_password_validate/<uidb64>/<token>', reset_password_validate,name='reset_password_validate' ),
    path('logout', logout,name='logout' ),
    path('reset_password', reset_password,name='reset_password' ),
    path('', dashboard,name='dashboard' ),
    path('my_orders/', my_orders,name='my_orders' ),
    path('edit_profile/', EditProfile,name='edit_profile' ),
    path('order_details/<str:order_id>/', order_detail,name='order_detail' ),
    path('change_password/', change_password,name='change_password' ),
    path('activate/<uidb64>/<token>', activate_email,name='activate' ),
    
]