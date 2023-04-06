from django.urls import path

from online_loan_app import views
from online_loan_app.customer.customer import create_new_customer, update_customer_details
from online_loan_app.user.user import create_new_user


urlpatterns = [
    path('login', views.login,name="login"),
    path('register', views.register, name='register'),
    path('user/create_new_user', create_new_user),
    path('user/update_user_details', create_new_user),
    path('customer/create_new_customer', create_new_customer),
    path('customer/update_customer_details', update_customer_details),
]