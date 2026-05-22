from django.apps import AppConfig


class HomeConfig(AppConfig):
    name = 'home'

    def ready(self):
        from django.contrib.auth.models import User
        def get_cart_count(self):
         from .models import CartItem
         return CartItem.objects.filter(cart__is_paid = False, cart__user = self).count()

        User.add_to_class("get_cart_count", get_cart_count)