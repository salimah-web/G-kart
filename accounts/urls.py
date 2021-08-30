from django.urls import path
from .views import register, sign_in, logout, activate_email, dashboard,forgot_password,reset_password_validate,reset_password
urlpatterns = [
    path('register', register,name='register' ),
    path('signin/', sign_in,name='signin' ),
    path('forgot_password', forgot_password,name='forgot_password' ),
    path('reset_password_validate/<uidb64>/<token>', reset_password_validate,name='reset_password_validate' ),
    path('logout', logout,name='logout' ),
    path('reset_password', reset_password,name='reset_password' ),
    path('dashboard', dashboard,name='dashboard' ),
    path('activate/<uidb64>/<token>', activate_email,name='activate' ),
    
]