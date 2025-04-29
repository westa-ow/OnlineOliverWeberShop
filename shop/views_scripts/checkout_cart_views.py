import concurrent
import csv
import uuid
from django.contrib.auth.decorators import login_required
from reportlab.lib import colors
from background_task import background
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from shop.decorators import login_required_or_session, logout_required, not_logged_in, ratelimit_with_logging
from shop.recaptcha_utils import verify_recaptcha
from shop.views import db, orders_ref, serialize_firestore_document, itemsRef, get_cart, cart_ref, single_order_ref, \
    get_user_category, get_user_session_type, metadata_ref, users_ref, update_email_in_db, get_user_prices, \
    get_user_info, get_address_info, get_vat_info, get_shipping_price, get_order, get_order_items, \
    active_promocodes_ref, active_cart_coupon, get_active_coupon, delete_user_coupons, used_promocodes_ref, \
    mark_user_coupons_as_used, get_user_sale, productGroups, get_vocabulary_product_card
import ast
import random
from datetime import datetime
from random import randint
from reportlab.platypus import Image
import concurrent.futures
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model, update_session_auth_hash
import os
import json
import firebase_admin
from django.utils.translation import gettext as _, get_language, activate
from django.views.decorators.csrf import csrf_exempt
from firebase_admin import credentials, firestore
from django.conf import settings
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.mail import send_mail, EmailMessage

from shop.forms import UserRegisterForm, User
import os
import json
import time
import logging
import tempfile
from datetime import datetime, timedelta, time
from subprocess import run
from io import BytesIO, StringIO
import urllib.request
import ftplib
from django.views.generic import TemplateView
# Django imports
from django.conf import settings
from django.contrib.auth import authenticate, login
from django.http import HttpResponse, JsonResponse, FileResponse
from django.shortcuts import render, redirect
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string

# Third-party imports

import firebase_admin
from firebase_admin import credentials, firestore
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch, cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer

from shop.views_scripts.auth_views import get_new_user_id, get_all_errors
from shop.views_scripts.profile_views import get_user_addresses, make_json_serializable

vats = {'Afghanistan': 0, 'Åland Islands': 0, 'Albania': 0, 'Algeria': 0, 'American Samoa': 0, 'Andorra': 0, 'Angola': 0, 'Anguilla': 0, 'Antarctica': 0, 'Antigua and Barbuda': 0, 'Argentina': 0, 'Armenia': 0, 'Aruba': 0, 'Australia': 0, 'Austria': 20, 'Azerbaijan': 0, 'Bahamas': 0, 'Bahrain': 0, 'Bangladesh': 0, 'Barbados': 0, 'Belarus': 0, 'Belgium': 21, 'Belize': 0, 'Benin': 0, 'Bermuda': 0, 'Bhutan': 0, 'Bolivia': 0, 'Bosnia and Herzegovina': 0, 'Botswana': 0, 'Bouvet Island': 0, 'Brazil': 0, 'British Indian Ocean Territory': 0, 'Brunei': 0, 'Bulgaria': 20, 'Burkina Faso': 0, 'Burma (Myanmar)': 0, 'Burundi': 0, 'Cambodia': 0, 'Cameroon': 0, 'Canada': 0, 'Cape Verde': 0, 'Cayman Islands': 0, 'Central African Republic': 0, 'Chad': 0, 'Chile': 0, 'China': 0, 'Christmas Island': 0, 'Cocos (Keeling) Islands': 0, 'Colombia': 0, 'Comoros': 0, 'Congo, Dem. Republic': 0, 'Congo, Republic': 0, 'Cook Islands': 0, 'Costa Rica': 0, 'Croatia': 25, 'Cuba': 0, 'Cyprus': 19, 'Czech Republic': 21, 'Denmark': 25, 'Djibouti': 0, 'Dominica': 0, 'Dominican Republic': 0, 'East Timor': 0, 'Ecuador': 0, 'Egypt': 0, 'El Salvador': 0, 'Equatorial Guinea': 0, 'Eritrea': 0, 'Estonia': 22, 'Ethiopia': 0, 'Falkland Islands': 0, 'Faroe Islands': 0, 'Fiji': 0, 'Finland': 24, 'France': 20, 'French Guiana': 0, 'French Polynesia': 0, 'French Southern Territories': 0, 'Gabon': 0, 'Gambia': 0, 'Georgia': 0, 'Germany': 19, 'Ghana': 0, 'Gibraltar': 0, 'Greece': 24, 'Greenland': 0, 'Grenada': 0, 'Guadeloupe': 0, 'Guam': 0, 'Guatemala': 0, 'Guernsey': 0, 'Guinea': 0, 'Guinea-Bissau': 0, 'Guyana': 0, 'Haiti': 0, 'Heard Island and McDonald Islands': 0, 'Honduras': 0, 'HongKong': 0, 'Hungary': 27, 'Iceland': 0, 'India': 0, 'Indonesia': 0, 'Iran': 0, 'Iraq': 0, 'Ireland': 23, 'Israel': 0, 'Italy': 22, 'Ivory Coast': 0, 'Jamaica': 0, 'Japan': 0, 'Jersey': 0, 'Jordan': 0, 'Kazakhstan': 0, 'Kenya': 0, 'Kiribati': 0, 'Dem. Republic of Korea': 0, 'Kuwait': 0, 'Kyrgyzstan': 0, 'Laos': 0, 'Latvia': 21, 'Lebanon': 0, 'Lesotho': 0, 'Liberia': 0, 'Libya': 0, 'Liechtenstein': 8.1, 'Lithuania': 21, 'Luxemburg': 0, 'Macau': 0, 'Macedonia': 0, 'Madagascar': 0, 'Malawi': 0, 'Malaysia': 0, 'Maldives': 0, 'Mali': 0, 'Malta': 18, 'Man Island': 0, 'Marshall Islands': 0, 'Martinique': 0, 'Mauritania': 0, 'Mauritius': 0, 'Mayotte': 0, 'Mexico': 0, 'Micronesia': 0, 'Moldova': 0, 'Monaco': 20, 'Mongolia': 0, 'Montenegro': 0, 'Montserrat': 0, 'Morocco': 0, 'Mozambique': 0, 'Namibia': 0, 'Nauru': 0, 'Nepal': 0, 'Netherlands': 21, 'Netherlands Antilles': 0, 'New Caledonia': 0, 'New Zealand': 0, 'Nicaragua': 0, 'Niger': 0, 'Nigeria': 0, 'Niue': 0, 'Norfolk Island': 0, 'Northern Ireland': 0, 'Northern Mariana Islands': 0, 'Norway': 0, 'Oman': 0, 'Pakistan': 0, 'Palau': 0, 'Palestinian Territories': 0, 'Panama': 0, 'Papua New Guinea': 0, 'Paraguay': 0, 'Peru': 0, 'Philippines': 0, 'Pitcairn': 0, 'Poland': 23, 'Portugal': 23, 'Puerto Rico': 0, 'Qatar': 0, 'Reunion Island': 0, 'Romania': 19, 'Russian Federation': 0, 'Rwanda': 0, 'Saint Barthelemy': 0, 'Saint Kitts and Nevis': 0, 'Saint Lucia': 0, 'Saint Martin': 0, 'Saint Pierre and Miquelon': 0, 'Saint Vincent and the Grenadines': 0, 'Samoa': 0, 'San Marino': 0, 'São Tomé and Príncipe': 0, 'Saudi Arabia': 0, 'Senegal': 0, 'Serbia': 0, 'Seychelles': 0, 'Sierra Leone': 0, 'Singapore': 0, 'Slovakia': 20, 'Slovenia': 22, 'Solomon Islands': 0, 'Somalia': 0, 'South Africa': 0, 'South Georgia and the South Sandwich Islands': 0, 'South Korea': 0, 'Spain': 21, 'Sri Lanka': 0, 'Sudan': 0, 'Suriname': 0, 'Svalbard and Jan Mayen': 0, 'Swaziland': 0, 'Sweden': 25, 'Switzerland': 8.1, 'Syria': 0, 'Taiwan': 0, 'Tajikistan': 0, 'Tanzania': 0, 'Thailand': 0, 'Togo': 0, 'Tokelau': 0, 'Tonga': 0, 'Trinidad and Tobago': 0, 'Tunisia': 0, 'Turkey': 0, 'Turkmenistan': 0, 'Turks and Caicos Islands': 0, 'Tuvalu': 0, 'Uganda': 0, 'Ukraine': 0, 'United Arab Emirates': 0, 'United Kingdom': 20, 'United States': 0, 'Uruguay': 0, 'Uzbekistan': 0, 'Vanuatu': 0, 'Vatican City State': 0, 'Venezuela': 0, 'Vietnam': 0, 'Virgin Islands (British)': 0, 'Virgin Islands (U.S.)': 0, 'Wallis and Futuna': 0, 'Western Sahara': 0, 'Yemen': 0, 'Zambia': 0, 'Zimbabwe': 0}


def generate_unique_order_id():
    """Generates a unique order identifier.
       Checks for availability in Firestore and regenerates if a duplicate is found.
    """
    while True:
        order_id = random.randint(1000000, 100000000)
        # Get all documents where the order_id matches the generated one
        existing_orders = list(orders_ref.where('order_id', '==', order_id).stream())
        if not existing_orders:
            return order_id

@login_required_or_session
def cart_page(request):
    email = get_user_session_type(request)
    category, currency = get_user_prices(request, email)
    if currency == "Euro":
        currency = "€"
    elif currency == "Dollar":
        currency = "$"

    info = get_user_info(email) or {}
    active_coupon = get_active_coupon(email)

    cart_products = sorted(get_cart(email), key=lambda x: x['number'])
    config = {'documents': cart_products}
    config_data = make_json_serializable(config)
    context = {
        'show_quantities': info.get("show_quantities", False),
        'sale': get_user_sale(info),
        'price_category': category,
        'vocabulary': get_vocabulary_product_card(),
        'documents': cart_products,
        'currency': currency,
        'active_coupon': active_coupon if len(active_coupon.keys()) != 0 else False,
        'config': config_data
    }

    return render(request, 'cart.html', context=context)


def sort_documents(request):
    order_by = request.GET.get('order_by', 'name')
    direction = request.GET.get('direction', 'asc')

    # Get documents from Firebase
    documents = get_cart(request.user.email)

    if order_by == 'sum':
        key_function = lambda x: x.get('price', 0) * x.get('quantity', 0)
    else:
        key_function = lambda x: x.get(order_by, "")

    sorted_documents = sorted(documents, key=key_function, reverse=(direction == 'desc'))

    return JsonResponse({'documents': sorted_documents})


@login_required
def send_email(request):
    if request.method == 'POST':
        # Create order

        language_code = request.path.split('/')[1]
        data = json.loads(request.body)
        vat = data.get('vat', 0)
        shippingValue = data.get('shipping', 0)
        shippingAddress = data.get('shippingAddress', '')
        billingAddress = data.get('billingAddress', 0)
        if billingAddress == 0:
            billingAddress = shippingAddress

        user_email = request.user.email

        category, currency = get_user_category(user_email) or ("Default", "Euro")

        active_coupon = get_active_coupon(user_email)
        print(active_coupon)
        checkout_admins_message = ""
        if active_coupon:
            checkout_admins_message = f"A customer with price category {category} ordered with promo code {active_coupon['coupon_code']} and discount {active_coupon['discount']}%"

        if active_coupon.get('single_use', False):
            mark_user_coupons_as_used(user_email)

        delete_user_coupons(user_email)

        cart = get_cart(user_email)

        order_id = generate_unique_order_id()
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
                "order_id": int(order_id),
                "order-id": int(order_id),
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
            'order_id': int(order_id),
            'order-id': int(order_id),
            'billingAddressId': billingAddress,
            'shippingAddressId': shippingAddress,
            'price': round(float(sum), 2),
            'shippingPrice': round(float(shippingValue), 2),
            'VAT': vat,
            'receipt_id': get_check_id(),
            'currency': currency,
            'payment_type': "BANK TRANSFER",
        }

        orders_ref.add(new_order)
        new_order['date'] = (new_order["date"]).isoformat()
        email_process(new_order, user_email, order_id, csv_content, language_code, checkout_admins_message)
        clear_all_cart(user_email)
        return JsonResponse({'status': 'success', 'redirect_name': 'home'})
    return JsonResponse({'status': 'error'}, status=400)



logger = logging.getLogger(__name__)


@background(schedule=60)
def email_process(new_order, user_email, order_id, csv_content, language_code, checkout_admins_message):
    try:
        activate(language_code)
        logger.info("Starting email_process")
        print("Starting email process")
        pdf_response = receipt_generator(new_order)
        if not pdf_response:
            print("PDF generation failed")
        logger.info("PDF generated successfully")
        print("PDF generated successfully")
        body_1 = _('''Dear Customer,

            Thank you for your purchase at Oliver Weber! We’re thrilled to have you as our customer.

            Your order has been successfully processed, and your receipt is attached to this email.
            Your Order Id''')
        body_2 = _('''Thank you for choosing Oliver Weber. We look forward to seeing you again!

            Best regards,  
            The Oliver Weber Team''')
        # Email creation
        email = EmailMessage(
            subject=_('Thank You for Your Order with Oliver Weber!'),
            body=f"""
            {body_1}: {order_id}.
            {body_2}
                """,
            from_email=settings.EMAIL_HOST_USER,
            to=[user_email],
        )
        email.attach(f'order_receipt_{order_id}.pdf', pdf_response, 'application/pdf')
        email.send()
        logger.info("Customer email sent successfully")

        # Server-side email
        email_server = EmailMessage(
            subject=f'{user_email} just ordered',
            body=f'Order info for {user_email}. {checkout_admins_message}',
            from_email=settings.EMAIL_HOST_USER,
            to=['westadatabase@gmail.com'],
        )

        email_server.attach(f'order_{order_id}.csv', csv_content, 'text/csv')
        email_server.attach(f'order_receipt_{order_id}.pdf', pdf_response, 'application/pdf')
        email_server.send()
        logger.info("Server email sent successfully")
    except Exception as e:
        logger.error(f"Error in email_process: {e}")
        print(f"Error in email_process: {e}")


def clear_all_cart(email):
    # Assuming `cart_ref` is defined and accessible within this scope
    docs = cart_ref.where('emailOwner', '==', email).stream()
    for doc in docs:
        doc.reference.delete()


def receipt_generator(order):
    # Assuming 'orders' contains the list of items in the cart
    # and 'order' contains details about the order itself

    buffer = BytesIO()

    make_pdf(order, buffer, True)

    # Preparing response
    pdf = buffer.getvalue()
    buffer.close()
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="order_{order.get("order_id", "unknown")}.pdf"'
    response.write(pdf)

    return pdf


def make_pdf(order, buffer, isWithImgs):

    orders = get_order_items(order.get('order_id'))
    currency = order.get('currency', "Euro")
    currency = "€" if currency == "Euro" else "$"

    shipping_address = get_address_info(order.get('shippingAddressId', dict()))
    billing_address = get_address_info(order.get('billingAddressId', dict()))

    vat = order.get('VAT', 0)
    vat = round(int(vat)/100, 3)
    shippingValue = order.get('shippingPrice', 0)

    date_str = str(order['date'])
    date_obj = datetime.fromisoformat(date_str)

    # Apply the formatting
    formatted_date = date_obj.strftime('%Y-%m-%d %H:%M:%S')
    roboto_font_path = os.path.join(settings.BASE_DIR, "shop", "static", "fonts", "Roboto-Regular.ttf")
    pdfmetrics.registerFont(TTFont('Roboto', roboto_font_path))
    roboto_bold_font_path = os.path.join(settings.BASE_DIR, "shop", "static", "fonts", "Roboto-Bold.ttf")
    pdfmetrics.registerFont(TTFont('Roboto-Bold', roboto_bold_font_path))
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=18)
    elements = []

    # Logo
    logo_path = os.path.join(settings.BASE_DIR, "shop", "static", "images", "general", "main_logo_receipt.jpg")
    elements.append(Image(logo_path, width=180, height=60))
    elements.append(Spacer(1, 20))

    # Header
    styles = getSampleStyleSheet()
    title_style = styles["Heading1"]
    title_style.fontName = "Roboto"
    title_style.alignment = 1

    normal_style = styles["Normal"]
    normal_style.fontName = "Roboto"

    elements.append(Paragraph(_("Thank you for shopping with Oliver Weber Shop."), title_style))
    subtitle = _(
        "You'll find your Order Summary below. If you have any questions regarding your order, please contact us.")
    elements.append(Paragraph(subtitle, normal_style))
    elements.append(Spacer(1, 20))
    bold_style = styles["Normal"].clone('bold_style')  # Create a new style based on “Normal”
    bold_style.fontName = "Roboto-Bold"  # Specify the registered bold font
    bold_style.fontSize = 10  # Optionally, you can specify the font size
    bold_style.textColor = colors.black

    white_style = styles["Normal"]
    white_style.fontColor = colors.white
    white_style.fontName = "Roboto"

    # Tables
    order_data = [
        [Paragraph('<b>' + _("Order Status") + '</b>', bold_style), f"{order.get('Status', 'Processing')}"],
        [Paragraph('<b>'+_("Order")+'</b>', bold_style), f"{order.get('order_id')}"],
        [Paragraph('<b>' + _("Shipping Date") + '</b>', bold_style), f""],
        [Paragraph('<b>' + _("Receipt") + '</b>', bold_style), f"{order.get('receipt_id', '')}"],
        ["", ""],
        [Paragraph('<b>' + _("Customer Code") + '</b>', bold_style), f"{order.get('payment_type', '')}"],
        [Paragraph('<b>' + _("Date") + '</b>', bold_style), f"{formatted_date}"]
    ]

    # Data for second table
    contact_data = [
        [Paragraph("<b>Oliver Weber Collection</b>", bold_style), ""],
        ["", ""],
        [Paragraph('<b>' + _("Phone:")+ '</b>', bold_style), "+43 5223 41 881"],
        [Paragraph("Email:", bold_style), "office@oliverweber.at"]
    ]

    # Table creation
    order_table = Table(order_data, colWidths=[120, 180])  # Column width
    contact_table = Table(contact_data, colWidths=[80, 220])

    # Table styles
    order_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))

    contact_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('SPAN', (0, 0), (1, 0)),  # Merging a cell for a header
    ]))

    # Composition of tables on a single line
    composite_table_data = [[order_table, contact_table]]

    composite_table = Table(composite_table_data, colWidths=[250, 250])  # Total width

    # Setting a common style for the layout
    composite_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    elements.append(composite_table)
    elements.append(Spacer(1, 20))
    white_style = styles["Normal"]
    white_style.fontName = 'Roboto'  # Specify your font
    white_style.fontSize = 10
    white_style.textColor = colors.white

    paragraph_style = ParagraphStyle(
        name='Normal',
        fontName='Roboto',
        fontSize=10,
        leading=12,  # Line spacing
        wordWrap='CJK',  # Word transfer
    )

    # Adress
    address_data = [
        [Paragraph(_("Customer Billing Details"), white_style), Paragraph(_("Delivery Details"), white_style)],
        [_("Contact Phone") + f': {billing_address.get("phone", "")}',
         _("Ship-To Code") + f': {shipping_address.get("address_id", "")}'],
        [Paragraph(_("Billing Address") + ':', paragraph_style),
         Paragraph(
             _("Ship-To Name") + f': {shipping_address.get("first_name", "")} {shipping_address.get("last_name", "")}',
             paragraph_style)],
        [Paragraph(f"{billing_address.get('real_address', '')} {billing_address.get('address_complement', '')}",
                   paragraph_style),
        Paragraph(
             _("Shipping Address") + f": {shipping_address.get('real_address', '')} {shipping_address.get('address_complement', '')}",
             paragraph_style)],
        [Paragraph(f'{billing_address.get("city", "")}', paragraph_style),
         Paragraph(f'{shipping_address.get("city", "")}', paragraph_style)],
        [Paragraph(f'{billing_address.get("postal_code", "")}', paragraph_style),
         Paragraph(f"{shipping_address.get('postal_code', '')}", paragraph_style)],
        [Paragraph(f"{billing_address.get('country', '')}", paragraph_style),
         Paragraph(f"{shipping_address.get('country', '')}", paragraph_style)],
    ]

    address_table = Table(address_data, colWidths=[250, 250])
    address_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#003765")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, -1), 'Roboto'),  # Set the font for the whole table
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),  # Align the content to the top edge
    ]))

    elements.append(address_table)
    elements.append(Spacer(1, 20))

    # Appendix
    elements.append(Spacer(1, 20))

    # Table of products
    product_data = [ [Paragraph(_("Product"), white_style), Paragraph(_("Photo"), white_style),
         Paragraph(_("Item Details"), white_style), Paragraph(_("Quantity"), white_style),
         Paragraph(_("Unit Price"), white_style), Paragraph(_("Total"), white_style)]] if isWithImgs else [ [Paragraph(_("Product"), white_style),
         Paragraph(_("Item Details"), white_style), Paragraph(_("Quantity"), white_style),
         Paragraph(_("Unit Price"), white_style), Paragraph(_("Total"), white_style)]]
    for item_order in orders:
        if isWithImgs:
            image_path = item_order['image-url']  # Adjust this line to get the actual image path or object
            image = Image(image_path)
            image.drawHeight = 50  # Example height in points
            image.drawWidth = 50
            row = [item_order['name'], image, item_order['description'], item_order['quantity'],
                   currency + f"{(item_order['price']):.2f}",
                   currency + f"{(round(item_order['price'] * item_order['quantity'], 2)):.2f}"]
        else:
            row = [item_order['name'], item_order['description'], item_order['quantity'],
                   currency + f"{item_order['price']:.2f}",
                   currency + f"{(round(item_order['price'] * item_order['quantity'], 2)):.2f}"]
        product_data.append(row)
    product_table = Table(product_data)
    product_table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#003765")),
                                       ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                                       ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
                                       ]))

    elements.append(product_table)
    elements.append(Spacer(1, 20))

    # Total amount
    total_price = round(order.get('price', 0), 2)
    product_price = round(total_price / (1 + vat), 2)
    shippingPrice = round(shippingValue / (1+vat), 2)
    shipping_vat = round(shippingValue - shippingPrice, 2)
    vat_price = round(total_price - product_price, 2)

    formatted_total_price = f"{product_price:.2f}"
    formatted_shipping_price = f"{shippingPrice:.2f}"
    formatted_shipping_price_vat = f"{shipping_vat:.2f}"
    formatted_vat_price = f"{vat_price:.2f}"
    formatted_full_price = f"{total_price+shippingValue:.2f}"
    bold_style1 = styles["Normal"].clone('bold_style1')  # Create a copy of the style
    bold_style1.fontName = "Roboto-Bold"  # Specify a bold font
    bold_style1.fontSize = 10  # Font size
    bold_style1.textColor = colors.black
    summary_data = [
        [Paragraph('<b>' + _('Subtotal') + '</b>', bold_style1), f"{currency}{formatted_total_price}"],
        [Paragraph("<b>" + _('Shipping price') + "</b>", bold_style1), f"{currency}{formatted_shipping_price}"],
        [Paragraph("<b>" + _('Shipping VAT') + "</b>", bold_style1), f"{currency}{formatted_shipping_price_vat}"],
        [Paragraph("<b>VAT</b>", bold_style1), f"{currency}{formatted_vat_price}"],
        [Paragraph("<b>" + _("TOTAL") + "</b>", bold_style1), f"{currency}{formatted_full_price}"],
    ]

    # Create a table
    summary_table = Table(summary_data, colWidths=[100, 100])  # Column width

    # Table styles
    summary_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),  # Aligning text in cells
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),  # Text font
        ('FONTSIZE', (0, 0), (-1, -1), 10),  # Font size
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),  # Bottom indent
        # ('LINEBELOW', (0, 1), (-1, 1), 1, colors.black),  # Line under the SHIPPING price line
        ('LINEBELOW', (0, 3), (-1, 3), 1, colors.black),  # The line under the VAT line
        ('LINEBELOW', (0, 4), (-1, 4), 1.5, colors.black),  # Line under the TOTAL line
    ]))

    # Adding a table indented to the right
    table_wrapper = Table([[summary_table]], colWidths=[doc.width])  # External table for indentation
    table_wrapper.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),  # Aligning the entire table to the right edge
    ]))

    # Adding a table to elements
    elements.append(table_wrapper)
    doc.build(elements)

    return buffer


def get_check_id():
    @firestore.transactional
    def increment_check_id(transaction, check_counter_ref):
        snapshot = check_counter_ref.get(transaction=transaction)
        last_check_id = snapshot.get('lastCheck') if snapshot.exists else 10000
        new_check_id = last_check_id + 1
        transaction.update(check_counter_ref, {'lastCheck': new_check_id})
        return new_check_id

    check_counter_ref = metadata_ref.document('checkCounter')
    transaction = db.transaction()
    new_check_id = increment_check_id(transaction, check_counter_ref)
    return new_check_id


@logout_required
def anonym_cart_info(request):

    email = get_user_session_type(request)
    category, currency = get_user_prices(request,email)
    if currency == "Euro":
        currency = "€"
    elif currency == "Dollar":
        currency = "$"
    form_register = UserRegisterForm()
    form_login = AuthenticationForm()
    print(form_register)
    context = {
        'documents': sorted(get_cart(email), key=lambda x: x['number']),
        'currency': currency,
        'form_register':form_register,
        'form_login':form_login,
        'error_messages': [],
        'RECAPTCHA_SITE_KEY': settings.RECAPTCHA_SITE_KEY,
    }

    return render(request, 'checkout/Checkout_Account_Auth.html', context=context)


@not_logged_in
def login_anonym_cart_info(request):
    email1 = get_user_session_type(request)
    documents = sorted(get_cart(email1), key=lambda x: x['number'])
    category, currency = get_user_prices(request, email1)
    if currency == "Euro":
        currency_symbol = "€"
    elif currency == "Dollar":
        currency_symbol = "$"
    else:
        currency_symbol = currency

    if request.method == 'POST':
        form_login = AuthenticationForm(request, request.POST)

        locked_until = request.session.get('axes_locked_until')
        if locked_until:
            now = time.time()
            if now < locked_until:
                unlock_time = datetime.fromtimestamp(locked_until).strftime('%H:%M:%S')
                form_login.add_error(
                    None,
                    f"Your account is locked due to too many failed login attempts. "
                    f"Please try again after {unlock_time}."
                )
            else:
                request.session.pop('axes_locked_until', None)

        if form_login.is_valid():
            username = form_login.cleaned_data['username']
            password = form_login.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user:
                email2 = user.email

                docs = users_ref.where('email', '==', email2).limit(1).get()
                if docs and not docs[0].to_dict().get('Enabled', True):
                    form_login.add_error(None, "Your account has been disabled.")
                else:
                    login(request, user)
                    update_email_in_db(email1, email2)
                    return redirect('checkout_addresses')
    else:
        form_login = AuthenticationForm()

    form_register = UserRegisterForm()

    return render(request, 'checkout/Checkout_Account_Auth.html', {
        'documents': documents,
        'currency': currency_symbol,
        'form_login': form_login,
        'form_register': form_register,
        'error_messages': get_all_errors([form_login, form_register]),
        'RECAPTCHA_SITE_KEY': settings.RECAPTCHA_SITE_KEY,
    })

@not_logged_in
@ratelimit_with_logging(key='ip', rate='5/m', block=True)
def register_anonym_cart_info(request):
    email_before = get_user_session_type(request)
    documents = sorted(get_cart(email_before), key=lambda x: x['number'])
    category, currency = get_user_prices(request, email_before)
    currency_symbol = {'Euro': '€', 'Dollar': '$'}.get(currency, currency)

    # 2) Инициализируем формы
    form_register = UserRegisterForm(request.POST or None)
    form_login = AuthenticationForm()

    # 3) Обработка POST-запроса (регистрация)
    if request.method == 'POST':
        # 3.1 Проверяем reCAPTCHA
        recaptcha_response = request.POST.get('g-recaptcha-response')
        if not verify_recaptcha(recaptcha_response):
            form_register.add_error(None, 'Invalid reCAPTCHA. Please try again.')
            logger.error(
                "Registration failed: invalid reCAPTCHA. Errors: %s",
                form_register.errors.as_json()
            )
        # 3.2 Если reCAPTCHA ок и форма валидна — проверяем уникальность email
        elif form_register.is_valid():
            email_after = form_register.cleaned_data['email']
            existing = users_ref.where('email', '==', email_after).limit(1).get()
            if existing:
                form_register.add_error('email', 'User with this email already exists.')
            else:
                # 3.3 Создаём запись в Firestore
                user_id    = get_new_user_id()
                now_str    = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                social     = "Mr" if form_register.cleaned_data.get('social_title') == "1" else "Mrs"
                offers     = form_register.cleaned_data['offers']
                newsletter = form_register.cleaned_data['receive_newsletter']
                cat, curr  = get_user_prices(request, email_after)
                new_user = {
                    'Enabled': True,
                    'display_name': 'undefined',
                    'social_title': social,
                    'first_name': form_register.cleaned_data['first_name'],
                    'last_name':  form_register.cleaned_data['last_name'],
                    'email':      email_after,
                    'birthday':   form_register.cleaned_data.get('birthdate'),
                    'price_category': cat,
                    'currency':       curr,
                    'receive_offers': offers,
                    'receive_newsletter': newsletter,
                    'registrationDate': now_str,
                    'userId':      user_id,
                    'sale':        0,
                    'customer_type': 'Customer',
                    'show_quantities': False,
                }
                users_ref.add(new_user)

                # 3.4 Создаём и сохраняем Django‑пользователя
                user = form_register.save(commit=False)
                # Генерируем уникальный username на основе email
                user.username = email_after
                # Устанавливаем пароль (UserCreationForm уже хэширует)
                user.set_password(form_register.cleaned_data['password1'])
                user.save()

                # 3.5 Аутентификация и очистка старой корзины
                user = authenticate(request, username=user.username,
                                    password=form_register.cleaned_data['password1'])
                if user:
                    clear_all_cart(email_after)
                    login(request, user)
                    update_email_in_db(email_before, email_after)
                    return redirect('checkout_addresses')

    # 4) Общий контекст и рендер одного шаблона
    context = {
        'documents':      documents,
        'currency':       currency_symbol,
        'form_login':     form_login,
        'form_register':  form_register,
        'error_messages': get_all_errors([form_register, form_login]),
        'RECAPTCHA_SITE_KEY': settings.RECAPTCHA_SITE_KEY,
    }
    print(context["RECAPTCHA_SITE_KEY"])
    return render(request, 'checkout/Checkout_Account_Auth.html', context)


def checkout_addresses(request):
    email = get_user_session_type(request)
    addresses, addresses_dict = get_user_addresses(email)

    category, currency = get_user_category(email) or ("Default", "Euro")
    if currency == "Euro":
        currency = "€"
    elif currency == "Dollar":
        currency = "$"
    info = get_user_info(email) or {}
    customer_type = info.get('customer_type', "Customer")
    form_register = UserRegisterForm()
    form_login = AuthenticationForm()
    active_coupon_data = get_active_coupon(email)
    active_coupon_data.pop('single_use', None)
    context = {
        'documents': sorted(get_cart(email), key=lambda x: x['number']),
        'currency': currency,
        'form_register': form_register,
        'form_login': form_login,
        'my_addresses': addresses,
        'addresses_dict': addresses_dict,
        'customer_type': customer_type,
        'STRIPE_PUBLISHABLE_KEY': settings.STRIPE_PUBLISHABLE_KEY,
        'activeCoupon': active_coupon_data,
    }
    return render(request, 'checkout/Checkout_Addresses.html', context=context)


def checkout_payment_type(request):
    email = get_user_session_type(request)

    category, currency = get_user_category(email) or ("Default", "Euro")
    if currency == "Euro":
        currency = "€"
    elif currency == "Dollar":
        currency = "$"
    addresses_properties_json = request.POST.get('addresses_properties')
    addresses_properties = json.loads(addresses_properties_json) if addresses_properties_json else {}
    context = {
        'documents': sorted(get_cart(email), key=lambda x: x['number']),
        'currency': currency,
        'STRIPE_PUBLISHABLE_KEY': settings.STRIPE_PUBLISHABLE_KEY,
        'addresses_properties': addresses_properties,
    }

    return render(request, 'checkout/Checkout_Payment_Type.html', context=context)


def check_promo_code(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        promo_code = data.get('promocode')
        email = get_user_session_type(request)
        if not promo_code or not email:
            return JsonResponse({'status': 'error', 'message': 'Please enter a promo code'})

        promo_code = promo_code.upper()  # Lowercase for consistency
        try:
            promocodes_ref = db.collection('Promocodes')
            query = promocodes_ref.where('code', '==', promo_code).limit(1).stream()
            promo_data = next(query, None)

            if promo_data is None:
                return JsonResponse({'status': 'error', 'message': 'Invalid promo code'})

            promo_dict = promo_data.to_dict()

            expiration_date = promo_dict.get('expiration_date')
            if expiration_date:
                # Преобразуем строку в datetime, предполагаем формат "YYYY-MM-DD"
                expires_at_date = datetime.strptime(expiration_date, "%Y-%m-%d")
                expires_at_date = datetime.combine(expires_at_date.date(), time(23, 59, 59))
                if datetime.now() > expires_at_date:
                    return JsonResponse({'status': 'error', 'message': 'Promo code is out of date'})

            b2b_only = promo_dict.get('b2b_only', False)
            customer_type = get_user_info(email).get('customer_type', 'Customer')
            if (b2b_only and customer_type == 'Customer') or (not b2b_only and customer_type == 'B2B'):
                return JsonResponse({'status': 'error', 'message': 'This promo code is not available.'})
            discount = promo_dict.get('discount', 0)

            # Checking that the discount is a number
            if not isinstance(discount, (int, float)):
                return JsonResponse({'status': 'error', 'message': 'Invalid discount value'})

            # If the user already has an active promo code, return an error message
            old_coupons = list(active_promocodes_ref.where('email', '==', email).stream())

            if old_coupons:
                return JsonResponse({
                    'status': 'error',
                    'message': 'You already have an active promo code. Please use or remove it before adding a new one.'
                })

            # If the promo code is disposable, check whether any user has used it before
            if promo_dict.get('single_use', False):
                used_promocodes = list(
                    used_promocodes_ref
                    .where('coupon_code', '==', promo_code)
                    .stream()
                )

                if used_promocodes:  # If there are entries, it means that some user has already used the promo code
                    return JsonResponse({
                        'status': 'error',
                        'message': 'This promo code has already been used.'
                    })

            new_coupon_id = str(uuid.uuid4())
            active_promocodes_ref.document(new_coupon_id).set({
                'email': email,
                'coupon_code': promo_code,
                'type': promo_dict.get('type'),
                'discount': discount,
                'single_use': promo_dict.get('single_use', False),
                'expiration_date': promo_dict.get('expiration_date'),  # If there's an expiration date
                'creation_date': datetime.now()
            })

            # Calculate the discount as a fractional value
            discount_rate = discount / 100.0

            active_cart_coupon(email)

            # Returning a successful result
            return JsonResponse({'status': 'success', 'message': 'Promo code is valid', 'discount_rate': discount_rate})

        except Exception as e:
            # Handling possible errors
            return JsonResponse({'status': 'error', 'message': f'Error checking promo code: {str(e)}'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

