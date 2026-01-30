from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, authenticate
from home.models import *

# Create your views here.

def home(request):
    pizzas = Pizza.objects.all()
    context = {'pizzas': pizzas}
    return render(request, 'home.html', context)

def login_page(request):
 if request.method == "POST":
    try:
        username = request.POST.get('username')
        password = request.POST.get('password')

        user_obj = User.objects.filter(username = username)
        if not user_obj.exists():
            messages.warning(request, "Invalid Username !!!")
            return redirect('/login/')

        user_obj = authenticate(username = username, password = password)
        #authenticate will return None if password is incorrect

        if user_obj:
           login(request, user_obj)
           return redirect('/')

        messages.error(request, "Wrong password !!!")


        return redirect('/login/')

    except Exception as e:
        messages.success(request, "Something went wrong !!!")

        return redirect('/register/')

 return render(request, "login.html")

def register_page(request):
 if request.method == "POST":
    try:
        username = request.POST.get('username')
        password = request.POST.get('password')

        user_obj = User.objects.filter(username = username)
        if user_obj.exists():
            messages.error(request, "Username alredy taken !!!")
            return redirect('/register/')

        user_obj = User.objects.create(username = username)
        user_obj.set_password(password)
        user_obj.save()

        messages.info(request, "User created successfully !!!")

        return redirect('/login/')

    except Exception as e:
        print(e)
        messages.success(request, "Something went wrong !!!")

        return redirect('/register/')

 return render(request, "register.html")

def add_card(request, pizza_uid):
   return redirect('/')
