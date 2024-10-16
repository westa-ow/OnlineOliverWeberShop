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
def create_checkout_session(request):
    if request.method == 'POST':
        domain_url = 'https://www.oliverweber.online/'  # Замените на ваш домен
        try:
            # Создаем сессию оплаты
            email = get_user_session_type(request)
            category, currency = get_user_prices(request, email)
            if currency == "Euro":
                currency = "eur"
            elif currency == "Dollar":
                currency = "usd"
            order_id = random.randint(1000000, 100000000)
            cart = get_cart(email)
            full_price = round(sum(item["price"] for item in cart), 2)
            metadata = {"Id": order_id, "email": email, "full_name": request.user.first_name + " " + request.user.last_name}

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

def stripe_checkout(request, order_id):
    # Создаю order
    data = json.loads(request.body)
    vat = int(data.get('vat', 0)) / 100

    user_email = request.user.email
    category, currency = get_user_category(user_email) or ("Default", "Euro")

    currency = '€' if currency == 'Euro' else '$'

    cart = get_cart(user_email)


    item_refs = []
    all_orders_info = []
    names = []
    sum = 0

    csv_output = StringIO()
    csv_writer = csv.writer(csv_output)
    csv_writer.writerow(['name', 'quantity'])

    for order_item in cart:
        description = order_item.get('description')
        price = order_item.get('price')
        quantity = order_item.get('quantity')
        name = order_item.get('name')
        names.append(name)
        image_url = order_item.get('image_url')
        sum += round(price * quantity, 1)
        new_order_item = {
            'description': description,
            "emailOwner": user_email,
            'image_url': image_url,
            'image-url': image_url,
            "name": name,
            "order_id": order_id,
            "order-id": order_id,
            "price": price,
            "quantity": quantity,
        }
        all_orders_info.append(new_order_item)
        doc_ref = single_order_ref.document()
        doc_ref.set(new_order_item)
        item_refs.append(doc_ref)

        csv_writer.writerow([name, quantity])

    csv_output.seek(0)
    csv_content = csv_output.getvalue()
    csv_output.close()

    new_order = {
        'Status': 'Awaiting',
        'date': datetime.now(),  # Current date and time
        'email': user_email,
        'list': [ref.path for ref in item_refs],  # Using document paths as references
        'order_id': order_id,
        'order-id': order_id,
        'price': round(sum, 1),
        'currency': 'Euro',
    }
    orders_ref.add(new_order)
    new_order['date'] = new_order['date'].isoformat()
    email_process(all_orders_info, new_order, currency, vat, user_email, order_id, csv_content,
                  request.user.first_name + " " + request.user.last_name)
    clear_all_cart(user_email)
    return sum

@csrf_exempt
def stripe_webhook(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    endpoint_secret = settings.STRIPE_ENDPOINT_SECRET
    payload = request.body.decode('utf-8')
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        print("PAYLOAD")
        logging.error(f"Invalid payload: {e}")
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        logging.error(f"Signature verification error: {e}")
        print("SIGNATURE")
        return HttpResponse(status=400)

    # Logging the event data
    logging.info(event)
    if event['type'] == 'checkout.session.completed':
        # Extract the session ID from the event data
        session_id = event['data']['object']['id']

        # Retrieve the metadata, including 'Id', from the session
        session = stripe.checkout.Session.retrieve(session_id)
        metadata = session.metadata

        # Access 'Id' from metadata and update Firestore
        order_id = metadata.get('Id')
        if order_id:
            query = orders_ref.where('order_id', '==', order_id).limit(1).stream()
            for doc in query:
                # Update the 'Status' field to 'Paid'
                doc.update({"Status": "Paid"})
                print(f"Order {order_id} has been marked as paid.")

    return HttpResponse(status=200)