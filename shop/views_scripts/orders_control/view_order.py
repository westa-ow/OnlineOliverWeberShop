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
import firebase_admin
from django.views.decorators.csrf import csrf_exempt
from firebase_admin import credentials, firestore
from django.conf import settings
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.mail import send_mail

from shop.forms import UserRegisterForm, User
from shop.views import addresses_ref, cart_ref, get_user_category, serialize_firestore_document, users_ref, is_admin, \
    orders_ref, itemsRef, db
from shop.views import get_user_info


@login_required
@user_passes_test(is_admin)
def view_order(request, order_id):
    allOrders = orders_ref.get()  # Assuming orders_ref is correctly initialized to point to your orders collection

    orderDict = {}
    orderRefDict = {}
    for order in allOrders:
        orderData = order.to_dict()
        key = str(orderData.get('order-id') or orderData.get('order_id'))
        orderDict[key] = orderData
        orderRefDict[key] = order
    orderMain = {}
    if order_id in orderDict:
        orderMain = orderDict[order_id]
    # Find the specific order by ID
    specificOrderData = orderDict[order_id]
    specificOrderRef = orderRefDict[order_id]
    # Assuming you have a way to reference your 'Item' collection

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
            # Query for matching item by 'name'
            name = doc_data.get('name')
            real_item_query = itemsRef.where('name', '==', name).limit(1).get()
            item_from_storage = {}

            for it in real_item_query:
                item_from_storage = it.to_dict()

            itemData = item_from_storage
            # Add 'quantity_max' to the item's data and calculate 'total'
            if 'quantity' in doc_data and 'price' in doc_data:
                orderItems.append({
                    **doc_data,
                    'quantity_max': itemData.get('quantity'),  # Quantity from storage
                    'total': round(doc_data['quantity'] * doc_data.get('price', 0), 2)
                })
        else:
            print(f"Data for item could not be processed: {item}")

    user_email = specificOrderData['email']

    category, currency = get_user_category(user_email)
    info = get_user_info(user_email)
    del orderMain['list']

    print(orderMain)
    serialized_data =  (serialize_firestore_document(specificOrderRef))
    del serialized_data['list']
    context = {
        'feature_name': "view_order",
        'currency': "€" if currency == "Euro" else "$",
        'cart': [],
        'orders': [orderDict[order_id]],  # This might need adjustment based on your actual requirements
        'addresses': [],
        'user_info': info,
        'user_orders': orderItems,  # Add order items to context
        'Order': serialized_data,
    }
    return render(request, 'admin_tools.html', context)