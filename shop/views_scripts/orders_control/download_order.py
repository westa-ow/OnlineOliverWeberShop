import ast
import random
from datetime import datetime
from io import BytesIO
from random import randint

import concurrent.futures
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model, update_session_auth_hash
import os
import json
import csv
import firebase_admin
from django.views.decorators.csrf import csrf_exempt
from firebase_admin import credentials, firestore
from django.conf import settings
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.mail import send_mail

from shop.forms import UserRegisterForm, User
from shop.views import addresses_ref, cart_ref, get_user_category, serialize_firestore_document, users_ref, is_admin, \
    orders_ref, itemsRef, db
from shop.views import get_user_info
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch, cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image


@login_required
@user_passes_test(is_admin)
def download_csv_order(request, order_id):
    allOrders = orders_ref.get()

    orderDict = {}
    orderRefDict = {}
    for order in allOrders:
        orderData = order.to_dict()
        key = str(orderData.get('order-id') or orderData.get('order_id'))
        orderDict[key] = orderData
        orderRefDict[key] = order

    # Find the specific order by ID
    specificOrderData = orderDict[order_id]
    itemList = specificOrderData.get('list', [])

    # Assuming 'list' is the list of item names in the order
    orderItems = []
    for item in itemList:
        doc_data = None

        # If item is a string, assume it's a path to a Firestore document
        if isinstance(item, str):
            item_ref = db.document(item)
            doc = item_ref.get()
            if doc.exists:
                doc_data = doc.to_dict()
            else:
                print(f"Document at path {item} not found.")
        # If item is not a string, attempt to get the document data directly
        else:
            doc_data = item.get().to_dict() if item.get() else None

        if doc_data:
            # Add 'quantity_max' to the item's data and calculate 'total'
            if 'quantity' in doc_data and 'price' in doc_data:
                orderItems.append({
                    **doc_data,
                    'total': round(doc_data['quantity'] * doc_data.get('price', 0), 2)
                })
        else:
            print(f"Data for item could not be processed: {item}")
    # Prepare response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="order_{order_id}.csv"'.format(order_id)

    writer = csv.writer(response)
    writer.writerow(['product_number', 'quantity', 'price', 'total'])  # Writing the headers

    # Assuming 'list' contains the items in the order with 'name', 'quantity', 'price'
    for item in orderItems:
        product_number = item.get('name')
        quantity = item.get('quantity')
        price = item.get('price')
        total = item.get('total')
        writer.writerow([product_number, quantity, price, total])

    return response

@login_required
@user_passes_test(is_admin)
def download_pdf_no_img(request, order_id):
    allOrders = orders_ref.get()

    orderDict = {}
    orderRefDict = {}
    for order in allOrders:
        orderData = order.to_dict()
        key = str(orderData.get('order-id') or orderData.get('order_id'))
        orderDict[key] = orderData
        orderRefDict[key] = order

    # Find the specific order by ID
    specificOrderData = orderDict[order_id]
    itemList = specificOrderData.get('list', [])

    # Assuming 'list' is the list of item names in the order
    orderItems = []
    for item in itemList:
        doc_data = None

        # If item is a string, assume it's a path to a Firestore document
        if isinstance(item, str):
            item_ref = db.document(item)
            doc = item_ref.get()
            if doc.exists:
                doc_data = doc.to_dict()
            else:
                print(f"Document at path {item} not found.")
        # If item is not a string, attempt to get the document data directly
        else:
            doc_data = item.get().to_dict() if item.get() else None

        if doc_data:
            # Add 'quantity_max' to the item's data and calculate 'total'
            if 'quantity' in doc_data and 'price' in doc_data:
                orderItems.append({
                    **doc_data,
                    'total': round(doc_data['quantity'] * doc_data.get('price', 0), 2)
                })
        else:
            print(f"Data for item could not be processed: {item}")

    userEmail = orderItems[0].get('emailOwner', "")
    info = {}
    if userEmail:
        info = get_user_info(userEmail) or {}
    client_name = info.get('first_name', "") + " " + info.get('last_name', "")
    buffer = BytesIO()

    # Basic setup
    styles = getSampleStyleSheet()

    center_bold_style2 = ParagraphStyle('CenterBold', parent=styles['Heading2'], fontSize=18, alignment=1,
                                        fontName='Times-Bold')
    bold_style = ParagraphStyle('Bold', parent=styles['Normal'], fontSize=12, fontName='Times-Bold')
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=18)
    content = []
    content.append(Paragraph(f"Order N.: {order_id}", center_bold_style2))
    content.append(Spacer(1, 0.3 * inch))
    content.append(Paragraph(f"Client name: {client_name}", bold_style))
    content.append(Paragraph(f"Client email: {userEmail}", bold_style))

    currency = "€" if info.get("currency", "Euro") == "Euro" else "Dollar"

    table_data = [["Product", "Quantity", "Price per item", "Total"]]
    for item_order in orderItems:

        row = [item_order['name'], item_order['quantity'], currency + str(item_order['price']),
               currency + str(round(item_order['price'] * item_order['quantity'], 2))]
        table_data.append(row)

    table = Table(table_data, colWidths=[1.7 * inch, 1.7 * inch, 1.7 * inch, 1.7 * inch, 1.3 * inch])

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

    # Order items table

    doc.build(content)

    # Preparing response
    pdf = buffer.getvalue()
    buffer.close()
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="pdf_order_{order_id}_without_images.pdf"'
    response.write(pdf)

    return response

@login_required
@user_passes_test(is_admin)
def download_pdf_w_img(request, order_id):
    allOrders = orders_ref.get()

    orderDict = {}
    orderRefDict = {}
    for order in allOrders:
        orderData = order.to_dict()
        key = str(orderData.get('order-id') or orderData.get('order_id'))
        orderDict[key] = orderData
        orderRefDict[key] = order

    # Find the specific order by ID
    specificOrderData = orderDict[order_id]
    itemList = specificOrderData.get('list', [])

    # Assuming 'list' is the list of item names in the order
    orderItems = []
    for item in itemList:
        doc_data = None

        # If item is a string, assume it's a path to a Firestore document
        if isinstance(item, str):
            item_ref = db.document(item)
            doc = item_ref.get()
            if doc.exists:
                doc_data = doc.to_dict()
            else:
                print(f"Document at path {item} not found.")
        # If item is not a string, attempt to get the document data directly
        else:
            doc_data = item.get().to_dict() if item.get() else None

        if doc_data:
            # Add 'quantity_max' to the item's data and calculate 'total'
            if 'quantity' in doc_data and 'price' in doc_data:
                orderItems.append({
                    **doc_data,
                    'total': round(doc_data['quantity'] * doc_data.get('price', 0), 2)
                })
        else:
            print(f"Data for item could not be processed: {item}")

    userEmail = orderItems[0].get('emailOwner', "")
    info = {}
    if userEmail:
        info = get_user_info(userEmail) or {}
    client_name = info.get('first_name', "") +" "+ info.get('last_name', "")
    buffer = BytesIO()

    # Basic setup
    styles = getSampleStyleSheet()

    center_bold_style2 = ParagraphStyle('CenterBold', parent=styles['Heading2'], fontSize=18, alignment=1,
                                        fontName='Times-Bold')
    bold_style = ParagraphStyle('Bold', parent=styles['Normal'], fontSize=12, fontName='Times-Bold')
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=18)
    content = []
    content.append(Paragraph(f"Order N.: {order_id}", center_bold_style2))
    content.append(Spacer(1, 0.3 * inch))
    content.append(Paragraph(f"Client name: {client_name}", bold_style))
    content.append(Paragraph(f"Client email: {userEmail}", bold_style))

    currency = "€" if info.get("currency", "Euro") == "Euro" else "Dollar"

    table_data = [["Product", "Image", "Quantity", "Price per item", "Total"]]
    for item_order in orderItems:
        image_path = item_order['image-url']  # Adjust this line to get the actual image path or object
        image = Image(image_path)
        image.drawHeight = 50  # Example height in points
        image.drawWidth = 50
        row = [item_order['name'], image, item_order['quantity'], currency + str(item_order['price']),
               currency + str(round(item_order['price'] * item_order['quantity'], 2))]
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

    # Order items table

    doc.build(content)

    # Preparing response
    pdf = buffer.getvalue()
    buffer.close()
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="pdf_order_{order_id}_with_images.pdf"'
    response.write(pdf)

    return response
