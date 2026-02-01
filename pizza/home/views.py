from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from home.models import *

# Create your views here.
from django.contrib import messages
from instamojo_wrapper import Instamojo
from django.conf import settings
api = Instamojo(api_key= settings.API_KEY,
                auth_token= settings.AUTH_TOKEN , endpoint="https://test.instamojo.com/api/1.1/")



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

def add_cart(request, pizza_uid):
   user = request.user
   pizza_obj = Pizza.objects.get(uid = pizza_uid)
   cart , _ = Cart.objects.get_or_create(user = user, is_paid = False) #get the cart if exists otherwise create a new cart
   cart_item = CartItem.objects.create(
      cart = cart,
      pizza = pizza_obj,
   )
   return redirect('/')

# def cart(request):
#     try:
#         cart = Cart.objects.get(is_paid=False, user=request.user)
        
#         # 1. Call the API
#         response = api.payment_request_create(
#             amount=str(cart.get_cart_total()), # Ensure this is a string and > 9
#             purpose="Order",
#             buyer_name=request.user.username,
#             email="mishra27999@gmail.com",
#             redirect_url="http://127.0.0.1:8000/success/"
#         )

#         # 2. Check if 'payment_request' exists in the response
#         if 'payment_request' in response:
#             payment_url = response['payment_request']['longurl']
#             print(response)
#             context = {
#                 'carts': cart,
#                 'payment_url': payment_url
#             }
#             return render(request, "cart.html", context)
#         else:
#             # This catches the case where Instamojo returns an error message
#             print(f"Instamojo Error: {response}")
#             messages.error(request, "Instamojo API Error: " + str(response))
#             return redirect('/')

#     except Cart.DoesNotExist:
#         messages.warning(request, "Your cart is empty.")
#         return redirect('/')
#     except Exception as e:
#         # This catches the Timeout or Connection errors
#         print(f"System Error: {e}")
#         messages.error(request, "Server connection failed. Please try again.")
#         return redirect('/')

def cart(request):
   cart = Cart.objects.get(is_paid = False, user = request.user)
   context = {'carts': cart,}
   # response = api.payment_request_create(
   #    amount = cart.get_cart_total(),
   #    purpose = "Order",
   #    buyer_name = request.user.username,
   #    email = "mishra27999@gmail.com",
   #    redirect_url = "http://127.0.0.1:8000/success/"

   #  )
   # context = {'carts': cart,
   # 'payment_url': response['payment_request']['longurl']}



   return render(request, "cart.html", context)

def remove_cart_items(request, cart_item_uid):
   try:
    CartItem.objects.get(uid = cart_item_uid).delete()

    return redirect('/cart/')
   except Exception as e:
      print(e)

def orders(request):
   orders = Cart.objects.filter(is_paid = True, user = request.user)
   context = {'orders': orders}
   return render(request, "orders.html", context)

# def process_payement(request):