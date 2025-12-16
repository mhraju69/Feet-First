# views.py
import stripe
from django.conf import settings
stripe.api_key = settings.STRIPE_SECRET_KEY


def create_checkout_session(orders = None , payments = None, price = None ):

    if not orders or not price or not payments:
        raise Exception("No orders or payments provided")
    
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        mode="payment",
        line_items=[
            {
                "price_data": {
                    "currency": "eur",
                    "unit_amount": int(price * 100),
                    "product_data": {
                        "name": "Confirm your orders",
                    },
                },
                "quantity": 1 ,
            }
        ],
        success_url="http://localhost:8888/success/",
        cancel_url="http://localhost:8888/cancel/",
        metadata={
            "orders": str(orders),
            "payments": str(payments)
        }
    )

    return session.url
