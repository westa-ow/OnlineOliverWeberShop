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
    get_user_session_type, get_cart, orders_ref, single_order_ref
from shop.views_scripts.checkout_cart_views import clear_all_cart, email_process
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from django.http import JsonResponse, HttpResponse
from django.conf import settings
import paypalrestsdk
import json
import random
from datetime import datetime
from io import StringIO
import csv
import logging

from shop.views_scripts.stripe_views import stripe_checkout

paypalrestsdk.configure({
    "mode": settings.PAYPAL_MODE,  # "sandbox" или "live"
    "client_id": settings.PAYPAL_CLIENT_ID,
    "client_secret": settings.PAYPAL_CLIENT_SECRET,
})

class PayPalSuccessView(TemplateView):
    template_name = 'stripe/success.html'

# Страница отмены
class PayPalCancelledView(TemplateView):
    template_name = 'stripe/cancelled.html'
@csrf_exempt
def create_paypal_payment(request):
    if request.method == 'POST':
        domain_url = 'https://www.oliverweber.online/'  # Замените на ваш домен
        language_code = request.path.split('/')[1]
        try:
            data = json.loads(request.body.decode('utf-8'))
            email = get_user_session_type(request)
            category, currency = get_user_prices(request, email)

            if currency == "Euro":
                currency = "EUR"
            elif currency == "Dollar":
                currency = "USD"

            order_id = random.randint(1000000, 100000000)
            cart = get_cart(email)
            shipping = data.get('shipping', 0)
            full_price = round(sum(item["price"] for item in cart), 2)
            full_price = full_price + shipping
            shippingAddress = data.get('shippingAddress', '')
            billingAddress = data.get('billingAddress', 0)
            if billingAddress == 0:
                billingAddress = shippingAddress
            metadata = {"Id": order_id, "email": email, "full_name": request.user.first_name + " " + request.user.last_name, "vat": data.get('vat', 0), "shippingValue": shipping, "shippingAddress": shippingAddress, 'billingAddress': billingAddress, "lang_code": language_code}

            payment = paypalrestsdk.Payment({
                "intent": "sale",
                "payer": {
                    "payment_method": "paypal"
                },
                "redirect_urls": {
                    "return_url": domain_url + 'paypal/success/',
                    "cancel_url": domain_url + 'paypal/cancelled/'
                },
                "transactions": [{
                    "item_list": {
                        "items": [{
                            "name": f'Order {order_id}',
                            "sku": f'{order_id}',
                            "price": str(full_price),
                            "currency": currency,
                            "quantity": 1
                        }]
                    },
                    "amount": {
                        "total": str(full_price),
                        "currency": currency
                    },
                    "custom": json.dumps(metadata),
                    "description": "Payment for order #" + str(order_id)
                }],
            })

            if payment.create():
                for link in payment['links']:
                    if link['rel'] == "approval_url":
                        approval_url = link['href']
                        return JsonResponse({'approval_url': approval_url})
            else:
                return JsonResponse({'error': payment.error}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return HttpResponse(status=405)

@csrf_exempt
def paypal_webhook(request):
    try:
        payload = json.loads(request.body.decode('utf-8'))
        event_type = payload.get('event_type')

        if event_type == 'PAYMENT.SALE.COMPLETED':
            # Получение данных о завершенном платеже
            sale = payload['resource']
            order_id = sale['invoice_number']
            metadata = sale.get('custom', {})

            # Обработка завершенного платежа
            if order_id:
                email = metadata.get('email')
                user_name = metadata.get('full_name')
                vat = metadata.get('vat', 0)
                shippingValue = metadata.get('shippingValue', 0)
                shippingAddress = metadata.get('shippingAddress', '')
                billingAddress = metadata.get('billingAddress', '')
                lang_code = metadata.get('lang_code', 'gb')
                stripe_checkout(email, user_name, order_id, vat, shippingValue, shippingAddress, billingAddress, "PAYPAL", lang_code)
                print(f"Order {order_id} has been marked as paid.")

        return HttpResponse(status=200)
    except Exception as e:
        logging.error(f"Webhook error: {e}")
        return HttpResponse(status=400)