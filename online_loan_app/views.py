from django.shortcuts import render
from rest_framework.decorators import api_view


# Create your views here.
def login(request):


    return render(request, 'login.html')


def register(request):
    return render(request, 'register.html')