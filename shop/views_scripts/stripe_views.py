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
    get_user_session_type, get_cart, orders_ref, single_order_ref, delete_user_coupons, get_active_coupon, \
    mark_user_coupons_as_used
from shop.views_scripts.checkout_cart_views import clear_all_cart, email_process, get_check_id
from shop.views_scripts.profile_orders_pay import stripe_partial_checkout

stripe.api_key = settings.STRIPE_SECRET_KEY

class SuccessView(TemplateView):
    """
    Stripe success page
    """
    template_name = 'stripe/success.html'


class CancelledView(TemplateView):
    """
    Stripe cancelled page
    """
    template_name = 'stripe/cancelled.html'

@csrf_exempt
def stripe_config(request):
    """
    Getting Stripe configuration
    """
    if request.method == 'GET':
        stripe_config = {'publicKey': settings.STRIPE_PUBLISHABLE_KEY}
        return JsonResponse(stripe_config, safe=False)

@csrf_exempt
@login_required
def create_checkout_session(request):
    """
    Creating payment checkout session for Stripe
    """
    if request.method == 'POST':
        domain_url = 'https://www.oliverweber.online/'
        if settings.CURRENT_DOMAIN == "oliverweber.com":
            domain_url = 'https://www.oliverweber.com/'
        elif settings.CURRENT_DOMAIN == "oliverweber.online":
            domain_url = 'https://www.oliverweber.online/'

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
            # Create a payment session
            email = get_user_session_type(request)
            category, currency = get_user_prices(request, email)
            if currency == "Euro":
                currency = "eur"
            elif currency == "Dollar":
                currency = "usd"
            order_id = random.randint(1000000, 100000000)
            cart = get_cart(email)
            full_price = round(sum(float(item["sum"]) for item in cart), 2)
            paid_sum = 0 + full_price
            full_price += shipping
            metadata = {"payment_type": "Stripe", "paid_sum": paid_sum, "Id": order_id, "email": email, "full_name": request.user.first_name + " " + request.user.last_name, "vat": data.get('vat', 0), "shippingPrice": shipping, "shippingAddress": shippingAddress, 'billingAddress': billingAddress, 'lang_code': language_code}

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
                                'name': f'{order_id}',  # Order id as a product name
                            },
                            'unit_amount': int(full_price * 100),  # Cost of goods in cents (2000 = $20.00)
                        },
                        'quantity': 1,
                    },
                ],
                metadata=metadata,
            )
            return JsonResponse({'id': checkout_session['id']})
        except Exception as e:
            return JsonResponse({'error': str(e)})

    # Processing for GET request or other methods
    return HttpResponse(status=405)


def stripe_checkout(email, user_name, order_id, vat, shippingPrice, shippingAddress, billingAddress, payment_type,
                    lang_code):
    """
    Stripe checkout function for creating orders document in database and sending email to user.
    """

    order_id = int(order_id)
    # Check if there is an order with this order_id
    existing_orders = orders_ref.where('order_id', '==', order_id).stream()
    if any(existing_orders):
        logging.info(f"Order {order_id} already exists. Skipping duplicate creation.")
        return 0  # Or return the current amount/status if needed

    # Next, the code for creating an order (calculating the amount, creating a record in the database, etc.)
    vat = int(vat)
    user_email = email
    category, currency = get_user_category(user_email) or ("Default", "Euro")

    active_coupon = get_active_coupon(email)
    checkout_admins_message = ""
    if active_coupon:
        checkout_admins_message = f"A customer with price category {category} ordered with promo code {active_coupon['coupon_code']} and discount {active_coupon['discount']}%"

    if active_coupon.get('single_use', False):
        mark_user_coupons_as_used(email)

    delete_user_coupons(email)
    cart = get_cart(user_email)

    item_refs = []
    all_orders_info = []
    names = []
    total_sum = 0

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
        total_sum += round(price * quantity, 1)
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
        'Status': 'Paid',
        'date': datetime.now(),
        'email': user_email,
        'list': [ref.path for ref in item_refs],
        'order_id': order_id,
        'order-id': order_id,
        'billingAddressId': billingAddress,
        'shippingAddressId': shippingAddress,
        'price': round(float(total_sum), 2),
        'shippingPrice': round(float(shippingPrice), 2),
        'VAT': vat,
        'receipt_id': get_check_id(),
        'currency': currency,
        'payment_type': payment_type,
    }
    orders_ref.add(new_order)
    new_order['date'] = new_order['date'].isoformat()
    email_process(new_order, user_email, order_id, csv_content, lang_code, checkout_admins_message)
    clear_all_cart(user_email)
    return total_sum

@csrf_exempt
def stripe_webhook(request):
    """
    Stripe webhook to handle checkout.session.completed events
    """
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
            # Update the 'Status' field to 'Paid'
            if metadata.get('payment_type') == "Stripe":
                stripe_checkout(metadata.get('email'), metadata.get('full_name'), order_id, metadata.get('vat'), metadata.get('shippingPrice'), metadata.get('shippingAddress'), metadata.get('billingAddress'), "STRIPE", metadata.get("lang_code", "gb"))
            elif metadata.get('payment_type') == "BANK TRANSFER":
                stripe_partial_checkout(metadata.get('email'), metadata.get('paid_sum'),  order_id, metadata.get("lang_code", "gb"))
            print(f"Order {order_id} has been marked as paid.")

    return HttpResponse(status=200)