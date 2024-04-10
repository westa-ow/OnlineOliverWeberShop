import ast
import random
from datetime import datetime
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
    response['Content-Disposition'] = 'attachment; filename="order_{}.csv"'.format(order_id)

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