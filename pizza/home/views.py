from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from home.models import *
from django.contrib import messages
from django.http import JsonResponse
import json
import uuid
import hmac
import hashlib
import base64
from django.shortcuts import render, redirect


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
        print(f"Payload: {data_to_sign}")
        print(f"Generated Signature: {signature}")
        return render(request, "cart.html", context)
    except Exception as e:
        print(f"Error: {e}")
        messages.error(request, "An unexpected error occurred.")
        return redirect('/')



def payment_failure(request):
    # Optional: You can log the failure or clear session data here
    # eSewa usually doesn't send data back to the failure URL in V2,
    # but it's good practice to have a general failure handler.
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

def add_cart(request, pizza_uid):
   user = request.user
   pizza_obj = Pizza.objects.get(uid = pizza_uid)
   cart , _ = Cart.objects.get_or_create(user = user, is_paid = False) #get the cart if exists otherwise create a new cart
   cart_item = CartItem.objects.create(
      cart = cart,
      pizza = pizza_obj,
   )
   return redirect('/')


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


# def cart(request):
#    cart = Cart.objects.get(is_paid = False, user = request.user)
#    context = {'carts': cart,}
#    response = api.payment_request_create(
#       amount = cart.get_cart_total(),
#       purpose = "Order",
#       buyer_name = request.user.username,
#       email = "mishra27999@gmail.com",
#       redirect_url = "http://127.0.0.1:8000/success/"

#     )
#    print(response)
#    context = {'carts': cart,
#    'payment_url': response['payment_request']['longurl']}



#    return render(request, "cart.html", context)

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