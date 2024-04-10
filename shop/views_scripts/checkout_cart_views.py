import concurrent

from django.contrib.auth.decorators import login_required
from reportlab.lib import colors

from shop.decorators import login_required_or_session
from shop.views import db, orders_ref, serialize_firestore_document, itemsRef, get_cart, cart_ref, single_order_ref, \
    get_user_category, get_user_session_type, metadata_ref
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
from datetime import datetime, timedelta
from subprocess import run
from io import BytesIO
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

@login_required_or_session
def cart_page(request):
    email = get_user_session_type(request)
    category, currency = get_user_category(email) or ("Default", "Euro")
    if currency == "Euro":
        currency = "€"
    elif currency == "Dollar":
        currency = "$"
    context = {
        'documents': sorted(get_cart(email), key=lambda x: x['number']),
        'currency': currency
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
        # Создаю order

        user_email = request.user.email
        category, currency = get_user_category(user_email) or ("Default", "Euro")

        currency = '€' if currency == 'Euro' else '$'

        cart = get_cart(request.user.email)

        user_email = request.user.email
        order_id = randint(1000000, 100000000)
        item_refs = []
        all_orders_info = []
        names = []
        sum = 0
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
        pdf_response = some_view(all_orders_info, new_order, "Test Name", currency)




        subject = 'Your Order Receipt'
        email_body = 'Here is your order receipt.'
        recipient_list = [user_email, 'westadatabase@gmail.com']

        email = EmailMessage(subject, email_body, settings.EMAIL_HOST_USER, recipient_list)
        email.attach(f'order_receipt_{order_id}.pdf', pdf_response, 'application/pdf')
        email.send()
        orders_ref.add(new_order)
        for delete_name in names:
            clear_cart(user_email, delete_name)
        return JsonResponse({'status': 'success', 'redirect_name': 'home'})
    return JsonResponse({'status': 'error'}, status=400)


def clear_cart(email, name):
    # Assuming `cart_ref` is defined and accessible within this scope
    docs = cart_ref.where('emailOwner', '==', email).where('name', '==', name).stream()
    for doc in docs:
        doc.reference.delete()


def some_view(orders, order, name, currency):
    # Assuming 'orders' contains the list of items in the cart
    # and 'order' contains details about the order itself
    buffer = BytesIO()

    # Basic setup
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle('Title', parent=styles['Title'], fontSize=24, alignment=1, spaceAfter=0.2 * inch)
    center_bold_style = ParagraphStyle('CenterBold', parent=styles['Normal'], fontSize=12, alignment=1,
                                       fontName='Times-Bold')
    center_bold_style2 = ParagraphStyle('CenterBold', parent=styles['Heading2'], fontSize=18, alignment=1,
                                       fontName='Times-Bold')
    bold_style = ParagraphStyle('Bold', parent=styles['Normal'], fontSize=12, fontName='Times-Bold')
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=18)
    content = []
    title_style = styles['Heading1']
    content.append(Paragraph("OLIVER WEBER COLLECTION", title_style))
    # content.append(Paragraph(f"Order {order['order_id']}", center_bold_style2))
    content.append(Spacer(1, 0.3 * inch))
    content.append(Paragraph(f"Client name: {name}", bold_style))

    table_data = [["Product","Image" ,"Quantity", "Price per item", "Total"]]
    for item_order in orders:
        image_path = item_order['image-url']  # Adjust this line to get the actual image path or object
        image = Image(image_path)
        image.drawHeight = 50  # Example height in points
        image.drawWidth = 50
        row = [item_order['name'], image, item_order['quantity'], currency + str(item_order['price']), currency + str(round(item_order['price'] * item_order['quantity'], 2))]
        table_data.append(row)

    table = Table(table_data, colWidths=[1.7 * inch, 1.0 * inch, 1.0 * inch, 1.7 * inch, 1.3 * inch])

    table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), '#f0f0f0'),
        ('TEXTCOLOR', (0, 0), (-1, 0), '#000000'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 1), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, 0), 'Times-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), '#ffffff'),
        ('GRID', (0, 0), (-1, -1), 1, '#000000')
    ])
    table.setStyle(table_style)
    content.append(Spacer(1, 1 * cm))

    content.append(table)

    # Order details
    email = order.get('email', 'No email provided')
    date = order.get('date', datetime.now()).strftime("%Y-%m-%d %H:%M:%S")

    total_price = round(order.get('price', 0), 2)
    content.append(Spacer(1, 0.5 * inch))
    content.append(Paragraph(f"Total paid(incl. VAT): {currency}{total_price}", bold_style))
    content.append(Paragraph(f"Included VAT: {currency}{round(order['price'] * 0.15,2)}", bold_style))
    content.append(Spacer(1, 0.3 * inch))
    content.append(Paragraph(f"Date: {date}", center_bold_style))
    content.append(Spacer(1, 10))
    content.append(Paragraph(f"E-mail: {email}", center_bold_style))
    content.append(Spacer(1, 10))
    content.append(Paragraph(f"DOCUMENT N.: {get_check_id()}", center_bold_style))
    content.append(Spacer(1, 10))
    content.append(Paragraph("Thank you for your purchase!", center_bold_style))
    # title_style = styles['Heading1']
    # body_style = styles['BodyText']


    # # Adding content
    # content.append(Paragraph("Order Receipt", title_style))
    # content.append(Spacer(1, 12))
    # content.append(Paragraph(f"Client Email: {email}", body_style))
    # content.append(Paragraph(f"Date: {date}", body_style))
    # content.append(Spacer(1, 12))

    # Order items table



    doc.build(content)

    # Preparing response
    pdf = buffer.getvalue()
    buffer.close()
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="order_{order.get("order_id", "unknown")}.pdf"'
    response.write(pdf)

    return pdf

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