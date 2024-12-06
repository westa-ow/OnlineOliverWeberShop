import csv
import logging
from datetime import datetime
import random
from io import StringIO

import stripe
from django.shortcuts import render, redirect
import json
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.generic import TemplateView

from OnlineShop import settings
from shop.views import addresses_ref, country_dict, users_ref, get_user_category, get_user_prices, \
    get_user_session_type, get_cart, orders_ref, single_order_ref, delete_user_coupons
from shop.views_scripts.checkout_cart_views import clear_all_cart, email_process, get_check_id
from django.utils.translation import gettext as _, get_language, activate
from django.core.mail import send_mail, EmailMessage

stripe.api_key = settings.STRIPE_SECRET_KEY

class SuccessView(TemplateView):
    template_name = 'stripe/success.html'

# Страница отмены
class CancelledView(TemplateView):
    template_name = 'stripe/cancelled.html'

@csrf_exempt
def stripe_config(request):
    if request.method == 'GET':
        stripe_config = {'publicKey': settings.STRIPE_PUBLISHABLE_KEY}
        return JsonResponse(stripe_config, safe=False)

@csrf_exempt
@login_required
def create_partial_checkout_session(request):
    if request.method == 'POST':
        domain_url = 'https://www.oliverweber.online/'  # Замените на ваш домен
        language_code = request.path.split('/')[1]
        stripe.api_key = settings.STRIPE_SECRET_KEY
        print(f"Stripe API Key: {settings.STRIPE_SECRET_KEY}")
        data = json.loads(request.body.decode('utf-8'))

        shippingAddress = data.get('shippingAddress', '')
        billingAddress = data.get('billingAddress', 0)
        shipping = data.get('shipping', 0)
        if billingAddress == 0:
            billingAddress = shippingAddress
        try:
            # Создаем сессию оплаты
            email = get_user_session_type(request)
            category, currency = get_user_prices(request, email)
            if currency == "Euro":
                currency = "eur"
            elif currency == "Dollar":
                currency = "usd"
            full_price = round(data.get('sum', 0), 2)
            order_id = int(data.get('order_id', 0))
            metadata = {"payment_type": "BANK TRANSFER", "Id": order_id, "email": email, "paid_sum": full_price, "full_name": request.user.first_name + " " + request.user.last_name, "shippingPrice": shipping, "shippingAddress": shippingAddress, 'billingAddress': billingAddress, 'lang_code': language_code}

            checkout_session = stripe.checkout.Session.create(
                success_url=domain_url + 'success/',
                cancel_url=domain_url + 'cancelled/',
                payment_method_types=['card'],
                mode='payment',
                line_items=[
                    {
                        'price_data': {
                            'currency': currency,
                            'product_data': {
                                'name': f'{order_id}',  # Название товара
                            },
                            'unit_amount': int(full_price * 100),  # Стоимость товара в центах (2000 = $20.00)
                        },
                        'quantity': 1,
                    },
                ],
                metadata=metadata,
            )
            return JsonResponse({'id': checkout_session['id']})
        except Exception as e:
            return JsonResponse({'error': str(e)})

    # Обработка для GET-запроса или других методов
    return HttpResponse(status=405)


def stripe_partial_checkout(email, paid_price, user_name, order_id, shippingAddress, billingAddress, payment_type, lang_code):
    # Создаю order
    user_email = email
    category, currency = get_user_category(user_email) or ("Default", "Euro")

    item_refs = []
    sum = 0
    order_id = int(order_id)
    order_query = orders_ref.where('order_id', '==', order_id).limit(1)
    order = None

    for doc in order_query.stream():
        order = doc
        break

    print(order)

    order_doc_ref = order.reference
    order_data = order.to_dict()
    current_paid_sum = order_data.get("paid_sum", 0)
    new_paid_sum = current_paid_sum + paid_price
    updates = {
        "paid_sum": new_paid_sum,
        "updated_at": datetime.now()  # Optional: Add a timestamp for tracking updates
    }

    order_doc_ref.update(updates)
    sent_email_confirmation(user_email, order_id, lang_code)
    return new_paid_sum

def sent_email_confirmation(user_email, order_id, language_code):
    try:
        activate(language_code)
        print("Starting email process")
        print("PDF generated successfully")
        body_1 = _('''Dear Customer,

            Your payment has been successfully processed.
            Your Order Id''')
        body_2 = _('''Thank you for choosing Oliver Weber. We look forward to seeing you again!

            Best regards,  
            The Oliver Weber Team''')
        # Email creation
        email = EmailMessage(
            subject=_('Your Payment Confirmation from Oliver Weber'),
            body=f"""
            {body_1}: {order_id}.
            {body_2}
                """,
            from_email=settings.EMAIL_HOST_USER,
            to=[user_email],
        )
        email.send()
        print("Customer email sent successfully")

        # Server-side email
        email_server = EmailMessage(
            subject=f'{user_email} just paid',
            body=f'Updated order info for {user_email}',
            from_email=settings.EMAIL_HOST_USER,
            to=['westadatabase@gmail.com'],
        )
        email_server.send()
        print("Server email sent successfully")
    except Exception as e:
        print(f"Error in email_process: {e}")
