from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from home.models import *
from django.contrib import messages
from django.http import JsonResponse
import json , uuid, hmac, base64, hashlib


def cart(request):
    if request.method == "POST":
        # Handle POST request logic here (if needed)
        return JsonResponse({"message": "POST method is not implemented yet."}, status=405)

    try:
        # Handle GET request logic
        cart_obj = Cart.objects.get(is_paid=False, user=request.user)

        # Explicitly cast to int then string to remove decimals
        total_amount = str(int(cart_obj.get_cart_total()))

        transaction_uuid = str(uuid.uuid4())
        cart_obj.transaction_id = transaction_uuid
        cart_obj.save()

        # Hardcoded values for testing
        product_code = "EPAYTEST"
        secret_key = "8gBm/:&EnhH.1/q"

        # Generate signature
        data_to_sign = f"total_amount={total_amount},transaction_uuid={transaction_uuid},product_code={product_code}"
        secret = bytes(secret_key, 'utf-8')
        message = bytes(data_to_sign, 'utf-8')
        hash = hmac.new(secret, message, hashlib.sha256).digest()
        signature = base64.b64encode(hash).decode("utf-8")
        context = {
            'carts': cart_obj,
            'total_amount': total_amount,
            'transaction_uuid': transaction_uuid,
            'product_code': product_code,
            'signature': signature,
        }
        return render(request, "cart.html", context)
    except Exception as e:
        print(f"Error: {e}")
        messages.error(request, "An unexpected error occurred.")
        return redirect('/')



def payment_failure(request):
    messages.error(request, "Payment was canceled or failed. Please try again.")
    return redirect('/cart/')

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

@login_required(login_url='/login/')
def add_cart(request, pizza_uid):
   user = request.user
   pizza_obj = Pizza.objects.get(uid = pizza_uid)
   cart , _ = Cart.objects.get_or_create(user = user, is_paid = False) #get the cart if exists otherwise create a new cart
   cart_item = CartItem.objects.create(
      cart = cart,
      pizza = pizza_obj,
   )
   return redirect('/')

@login_required(login_url='/login/')
def payment_success(request):
    encoded_data = request.GET.get('data')
    if encoded_data:
        try:
            decoded_bytes = base64.b64decode(encoded_data)
            decoded_data = json.loads(decoded_bytes.decode('utf-8'))

            # DEBUG: See what eSewa sent
            print(f"eSewa Data: {decoded_data}")

            if decoded_data.get('status') == 'COMPLETE':
                transaction_uuid = decoded_data.get('transaction_uuid')
                cart_obj = Cart.objects.filter(transaction_id=transaction_uuid).first()

                if cart_obj:
                    cart_obj.is_paid = True
                    cart_obj.save()
                    messages.success(request, "Payment Successful! Your order has been placed.")
                    print("SUCCESS: Message added to session.")
                else:
                    print(f"ERROR: No cart found with ID {transaction_uuid}")
        except Exception as e:
            print(f"CATCH ERROR: {e}")

    return redirect('/order/')

@login_required(login_url='/login/')
def remove_cart_items(request, cart_item_uid):
   try:
    CartItem.objects.get(uid = cart_item_uid).delete()

    return redirect('/cart/')
   except Exception as e:
      print(e)

@login_required(login_url='/login/')
def orders(request):
   orders = Cart.objects.filter(is_paid = True, user = request.user)
   context = {'orders': orders}
   return render(request, "orders.html", context)

def about(request):
    return render(request, 'about.html')

def feedback(request):
    if request.method == "POST":
        messages.success(request, "Thank you for your feedback!")
        return redirect('/feedback/')
    return render(request, 'feedback.html')

def contact(request):
    return render(request, "contact.html")

@login_required(login_url='/login/')
def logout(request):
    messages.success(request, "You have been logged out successfully.")
    return redirect('/')