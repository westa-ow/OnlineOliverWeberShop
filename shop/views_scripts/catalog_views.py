import concurrent

from django.contrib.auth.decorators import login_required

from shop.decorators import login_required_or_session
from shop.views import db, orders_ref, serialize_firestore_document, itemsRef, cart_ref, get_cart, favourites_ref, \
    get_user_category, get_user_info, get_user_session_type, get_vocabulary_product_card, get_user_prices
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

# categories = {
#     "3": "necklaces",
#     "74": "colliers",
#    "275": "pendants",
#     "76": "pearls",
#     "61": "rosegold-necklaces",
#     "62": "gold-necklaces",
#     "63": "rhodium-necklaces",
#     "64": "sterling-silver-necklaces",
#     "65": "zircon-necklaces",
#     "80": "stainless-steel-necklaces",
#     "4": "accessories",
#     "66": "pen",
#     "67": "brooch",
#     "7": "rings",
#     "20": "rosegold-rings",
#     "21": "gold-rings",
#     "22": "rhodium-rings",
#     "23": "sterling-silver-rings",
#     "24": "zircon-rings",
#     "81": "stainless-steel-rings",
#     "8": "earrings",
#     "208": "earrings",
#     "25": "studs",
#     "26": "drops",
#     "27": "hoops",
#     "28": "pearl",
#     "34": "rosegold-earrings",
#     "35": "gold-earrings",
#     "36": "rhodium-earrings",
#     "37": "sterling-silver-earrings",
#     "38": "zircon-earrings",
#     "82": "stainless-steel-earrings",
#     "9": "bracelets",
#     "39": "bangle",
#     "40": "chain",
#     "48": "rosegold-bracelets",
#     "50": "rhodium-bracelets",
#     "51": "sterling-silver-bracelets",
#     "52": "zircon-bracelets",
#     "83": "stainless-steel-bracelets",
#     "79": "anklets",
#     "84": "stainless-steel-anklets",
# }
categories = {
    "0": "All",
    "3": "Necklaces",
    "203": "Necklace",
    "74": "Colliers",
    "274": "Pendants",
    "76": "Pearls",
    "61": "rosegold-necklaces",
    "62": "gold-necklaces",
    "63": "rhodium-necklaces",
    "64": "sterling-silver-necklaces",
    "65": "zircon-necklaces",
    "80": "stainless-steel-necklaces",
    "4": "Accessories",
    "66": "Pen",
    "67": "Brooch",
    "267": "Nailfile",
    "7": "Ring",
    "20": "rosegold-rings",
    "21": "gold-rings",
    "22": "rhodium-rings",
    "23": "sterling-silver-rings",
    "24": "zircon-rings",
    "81": "stainless-steel-rings",
    "8": "All Earrings",
    "208": "Earrings",
    "2208": "Post Earrings",
    "25": "Studs",
    "26": "Drops",
    "27": "Hoops",
    "227": "Creole",
    "228": "Clips",
    "229": "Piercing",
    "28": "Pearl",
    "34": "rosegold-earrings",
    "35": "gold-earrings",
    "36": "rhodium-earrings",
    "37": "sterling-silver-earrings",
    "38": "zircon-earrings",
    "82": "stainless-steel-earrings",
    "9": "Bracelets",
    "209": "Bracelets",
    "39": "Bangle",
    "40": "Chain",
    "240": "Pearlchain",
    "48": "rosegold-bracelets",
    "50": "rhodium-bracelets",
    "51": "sterling-silver-bracelets",
    "52": "zircon-bracelets",
    "83": "stainless-steel-bracelets",
    "79": "Anklet",
    "2000": "Match",
    "2001": "Pen",
    "2002": "Key",
    "84": "stainless-steel-anklets",
    "2003": "Extension",
    "2004": "UV",
    "404": "NotFound",
}

@login_required_or_session
def catalog_view(request):
    category_catalog = request.GET.get('category') or ""
    collection_catalog = request.GET.get('collection') or ""
    plating_catalog = request.GET.get('plating') or ""
    base_catalog = request.GET.get('base') or ""
    email = get_user_session_type(request)
    category, currency = get_user_prices(request,email)
    info = get_user_info(email) or {}
    sale = round((0 if "sale" not in info else info['sale'])/100, 3) or 0

    show_quantities = info['show_quantities'] if 'show_quantities' in info else False
    context = {
        "currency": "€" if currency == "Euro" else "$",
        "category": category,
        "category_catalog": category_catalog,
        "collection_catalog": collection_catalog,
        "plating_catalog": plating_catalog,
        "base_catalog": base_catalog,
        'sale': sale,
        'show_quantities': show_quantities,
        'vocabulary': get_vocabulary_product_card()
    }
    return render(request, 'catalog.html', context=context)


@login_required_or_session
def param_catalog(request, category_id, category_name):
    if "-" in category_id:
        category_id, category_name = category_id.split("-", 1)  # Разделяет только по первому дефису

    collection_catalog = request.GET.get('collection') or ""
    plating_catalog = request.GET.get('plating') or ""
    base_catalog = request.GET.get('base') or ""
    email = get_user_session_type(request)
    category, currency = get_user_prices(request,email)
    info = get_user_info(email) or {}
    sale = round((0 if "sale" not in info else info['sale'])/100, 3) or 0

    show_quantities = info['show_quantities'] if 'show_quantities' in info else False
    context = {
        "currency": "€" if currency == "Euro" else "$",
        "category": category,
        "category_catalog": categories.get(category_id, "404"),
        "collection_catalog": collection_catalog,
        "plating_catalog": plating_catalog,
        "base_catalog": base_catalog,
        'sale': sale,
        'show_quantities': show_quantities,
        'vocabulary': get_vocabulary_product_card()
    }
    return render(request, 'catalog.html', context=context)


@csrf_exempt
@login_required_or_session
def add_to_cart_from_catalog(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        product_name = data.get('document')
        new_quantity = data.get('quantity')

        email = get_user_session_type(request)
        category, currency = get_user_prices(request, email)
        currency = '€' if currency == 'Euro' else '$'
        email = get_user_session_type(request)
        info = get_user_info(email) or {}
        sale = round((0 if "sale" not in info else info['sale'])/100, 3) or 0
        if not product_name or new_quantity is None:
            return JsonResponse({'status': 'error', 'message': 'Missing product name or quantity'}, status=400)

        document = get_full_product(product_name)
        if category == "VK3":
            document['price'] = document.get('priceVK3', 0)
        elif category == "GH":
            document['price'] = document.get('priceGH', 0)
        elif category == "Default USD":
            document['price'] = round(document.get('priceUSD', 0) * (1-sale), 1) or 0
        elif category == "GH_USD":
            document['price'] = document.get('priceUSD_GH', 0)
        else:
            document['price'] = round(document.get('priceVK4', 0) * (1-sale), 1) or 0
        if not document:
            return JsonResponse({'status': 'error', 'message': 'Product not found'}, status=404)

        subtotal, cart_size = update_cart(email, product_name, new_quantity, document)

        if subtotal is None:  # Assuming update_cart returns None on error
            return JsonResponse({'status': 'error', 'message': 'An error occurred while processing your request'},
                                status=500)
        return JsonResponse({
            'status': 'success',
            'quantity': new_quantity,
            'product_id': product_name,
            'sum': f"{round(new_quantity * document['price'], 2)}",
            'product': document,
            'cart_size': cart_size,
            'subtotal': f"{subtotal}"
        })
    else:
        return JsonResponse({'status': 'error', 'message': 'An error occurred while processing your request'},
                            status=500)


def get_full_product(catalog_product_name):
    docs = itemsRef.where('name', '==', catalog_product_name).where('Visible', '==', True).limit(1).stream()
    for doc in docs:
        return doc.to_dict()
    return None


def update_cart(email, product_name, new_quantity, document):
    existing_item = cart_ref.where('emailOwner', '==', email).where('name', '==', product_name).limit(1).get()
    cart_items = get_cart(email)  # This function needs to be defined or adjusted
    subtotal = sum(float(item['sum']) for item in cart_items)

    quantity_max = 0
    if 'pre_order' in document:
        quantity_max = 20 if document['pre_order'] else document['quantity']
    else:
        quantity_max = document['quantity']

    if existing_item:
        doc_ref = existing_item[0].reference
        doc_ref.update({'quantity': new_quantity})
        subtotal += round(new_quantity * document['price'], 2) - subtotal
    else:
        cart_ref.add({
            'description': document['description'],
            'stone': str(document['stone']),
            'material': document['material'],
            'plating': document['plating'],
            "emailOwner": email,
            'image_url': document['image-url'],
            "name": document['name'],
            "price": document['price'],
            "quantity": new_quantity,
            "number": len(cart_items) + 1,
            "product_name": document['product_name'],
            "category": document['category'],
            'quantity_max': quantity_max
        })
        subtotal += round(new_quantity * document['price'], 2)

    return round(subtotal, 2), len(cart_items) + (0 if existing_item else 1)


def change_favorite_state(request):
    if request.method == 'POST':

        data = json.loads(request.body)
        item = json.loads(data.get('item'))
        isFav = data.get('alreadyFavourite') == "true"

        # User's email from the request
        email = request.user.email

        if isFav:
            # Query for documents where email and name_id match to delete
            fav_docs = favourites_ref.where('email', '==', email).where('name', '==', item['name']).stream()

            # Iterate through the query results and delete each document
            for doc in fav_docs:
                doc.reference.delete()
            return JsonResponse({"isFavourite": "false", "item": json.dumps(item)})
        else:
            # Add a new favorite item to the database
            new_fav = item.copy()  # Assuming 'item' is a dictionary containing the necessary fields
            new_fav['email'] = email  # Add the user's email to the item
            favourites_ref.add(new_fav)

            return JsonResponse({"isFavourite": "true", "item": json.dumps(item)})
    return JsonResponse({"status": "error", 'message': 'Nonexistent method'})

