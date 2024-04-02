import concurrent

from django.contrib.auth.decorators import login_required

from shop.views import db, orders_ref, serialize_firestore_document, itemsRef, get_cart, cart_ref, single_order_ref, \
    get_user_category
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


@login_required
def cart_page(request):
    email = request.user.email
    category, currency = get_user_category(email)
    if currency == "Euro":
        currency = "€"
    elif currency == "Dollar":
        currency = "$"
    context = {
        'documents': sorted(get_cart(request.user.email), key=lambda x: x['number']),
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


def send_email(request):
    if request.method == 'POST':
        # Создаю order

        email = request.user.email
        category, currency = get_user_category(email)

        currency = '€' if currency == 'Euro' else '$'

        cart = get_cart(request.user.email)

        email = request.user.email
        order_id = randint(1000000, 100000000)
        item_refs = []
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
                "emailOwner": email,
                'image_url': image_url,
                "name": name,
                "order_id": order_id,
                "price": price,
                "quantity": quantity,
            }
            doc_ref = single_order_ref.document()
            doc_ref.set(new_order_item)
            item_refs.append(doc_ref)
        new_order = {
            'Status': 'Awaiting',
            'date': datetime.now(),  # Current date and time
            'email': email,
            'list': [ref.path for ref in item_refs],  # Using document paths as references
            'order_id': order_id,
            'order-id': order_id,
            'price': round(sum, 1),
            'currency': 'Euro',
        }
        orders_ref.add(new_order)

        for delete_name in names:
            clear_cart(email, delete_name)

        # Define email parameters
        subject = 'Test mail'
        message = 'Test mail from order-form!'
        recipient_list = [str(request.user.email), 'westadatabase@gmail.com']  # replace with your recipient list
        print(recipient_list)
        # Send the email
        send_mail(subject, message, 'setting.EMAIL_HOST_USER', recipient_list)
        return JsonResponse({'status': 'success', 'redirect_name': 'home'})
    return JsonResponse({'status': 'error'}, status=400)

def clear_cart(email, name):
    docs = cart_ref.where('emailOwner', '==', email).where('name', '==', name).stream()
    for doc in docs:
        doc.reference.delete()