from django.http import HttpResponse
from django.shortcuts import render
from rest_framework.decorators import api_view

from online_loan_app.database import get_mysql_connection
from online_loan_app.logs import Logger
from online_loan_app.user.user_controller import get_all_users

logger = Logger()


# Create your views here.
def login(request):
    if request.method == "POST":
        email = request.POST.get('email', None)
        user_password = request.POST.get('password', None)

        if (email == "admin@gmail.com") and (user_password == "admin"):
            logger.error('[{}]'.format('Request form-data were not provided.'))
            return HttpResponse("Login Success", status=200)
        else:
            return HttpResponse("Login Failed", status=404)

    return render(request, 'login.html')


def register(request):
    return render(request, 'register.html')
