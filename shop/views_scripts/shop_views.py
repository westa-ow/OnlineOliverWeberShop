import concurrent

from django.contrib.auth.decorators import login_required

from shop.views import db, orders_ref, serialize_firestore_document, itemsRef, get_cart, cart_ref
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
def form_page(request):
    documents = []
    search_term = ''
    if request.method == 'POST':
        search_term = request.POST.get('number').upper()

        documents = itemsRef.where('name', '==', search_term).stream()

    cart = get_cart(request.user.email)
    quantity = 1
    inside = False
    for prod in cart:
        if search_term == prod['name']:
            inside = True
            quantity = prod['quantity']
            break

    context = {
        'documents': [doc.to_dict() for doc in documents],
        'search_term': search_term,
        'inside': inside,
        'quantity': quantity,
        'is_authenticated': 'False',
        'in_cart': 'False',
        'cart': cart
    }

    return render(request, 'shop_page.html', context)

def fetch_numbers(request):
    search_term = request.GET.get('term', '').lower()
    numbers = []

    if search_term != '':
        # Using Firestore query to filter documents
        name_query = itemsRef.where('name', '>=', search_term).where('name', '<=', search_term + '\uf8ff').stream()

        # Filter the results in Python for the 'quantity' field
        numbers = [doc.to_dict().get('name', '') for doc in name_query if
                   search_term in doc.to_dict().get('name', '').lower() and
                   doc.to_dict().get('quantity', 0) > 0]

    return JsonResponse(numbers, safe=False)

