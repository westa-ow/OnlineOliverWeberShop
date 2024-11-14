import concurrent

from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from openpyxl import load_workbook

from shop.views import db, orders_ref, serialize_firestore_document, users_ref, addresses_ref, update_email_in_db, \
    get_user_category, get_user_info, get_vocabulary_product_card, get_user_prices, get_user_session_type
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
from django.utils.translation import gettext as _

from shop.views_scripts.catalog_views import update_cart, get_full_product


@login_required
def profile(request, feature_name):
    email = request.user.email
    orders = get_orders_for_user(email)
    print(orders)
    order_details = get_order_details(orders)
    email = request.user.email
    category, currency = get_user_prices(request,email)
    info = get_user_info(email) or {}
    show_quantities = info['show_quantities'] if 'show_quantities' in info else False
    if currency == "Euro":
        currency = "€"
    elif currency == "Dollar":
        currency = "$"

    if feature_name == 'order_import' or feature_name == "archive_search":
        if info.get('customer_type', 'Customer') != 'B2B':
            return redirect('profile', feature_name='dashboard')
    context = build_context(feature_name, email, orders, order_details)
    context['currency'] = currency
    context['userId'] = info['userId']
    context['username'] = info['first_name'] + " " + info['last_name']
    context['show_quantities'] = show_quantities


    return render(request, 'profile.html', context=context)

def get_orders_for_user(email):
    orders = []
    docs_orders = orders_ref.where('email', '==', email).stream()

    for doc in docs_orders:
        order_info = doc.to_dict()
        order_id = order_info.get('order_id') or order_info.get('order-id')
        formatted_date = format_date(order_info.get('date'))
        orders.append({
            'Status': order_info.get('Status'),
            'date': formatted_date,
            'email': email,
            'list': order_info.get('list'),
            'order_id': order_id,
            'sum': order_info.get('price')
        })
    orders.sort(key=lambda x: x['date'], reverse=True)
    return orders

def format_date(date_obj):
    return date_obj.strftime("%Y-%m-%d") if date_obj else None

def get_order_details(orders):
    order_details = {order['order_id']: [] for order in orders}

    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_order = schedule_order_detail_fetching(executor, orders, order_details)
        for future in concurrent.futures.as_completed(future_to_order):
            order_id = future_to_order[future]
            order_doc_data = future.result()
            if order_doc_data:
                order_details[order_id].append(order_doc_data)

    return order_details

def schedule_order_detail_fetching(executor, orders, order_details):
    future_to_order = {}
    for order in orders:
        for order_doc_ref in order['list']:
            order_doc_path = order_doc_ref if type(order_doc_ref) is str else order_doc_ref.path
            future = executor.submit(fetch_order_detail, order_doc_path)
            future_to_order[future] = order['order_id']
    return future_to_order

def fetch_order_detail(order_doc_path):
    path_parts = order_doc_path.split('/')
    if len(path_parts) == 2:
        collection_name, document_id = path_parts
        order_doc_ref = db.collection(collection_name).document(document_id)
        order_doc = order_doc_ref.get()
        if order_doc.exists:
            return order_doc.to_dict()
    return None

def build_context(feature_name, email, orders, order_details):
    currencies_dict ={}
    for order in orders:
        currencies_dict[order['order_id'] if 'order_id' in order.keys() else order['order-id']] = "€" if (order['currency'] if 'currency' in order else "Euro")=="Euro" else "$"

    context = {
        'currencies': currencies_dict,
        'orders': orders,
        'products': order_details,
        'feature_name': feature_name,
        'vocabulary': get_vocabulary_product_card()
    }

    if feature_name == "account":
        context['user_info'], context['user_info_dict'] = get_user_info_dicts(email)

    if feature_name == "addresses":
        addresses, addresses_dict = get_user_addresses(email)
        context['my_addresses'] = addresses
        context['addresses_dict'] = addresses_dict

    return context

def get_user_info_dicts(email):
    existing_users = users_ref.where('email', '==', email).limit(1).get()
    if existing_users:
        for user in existing_users:
            user_ref = users_ref.document(user.id)
            user_data = serialize_firestore_document(user_ref.get())
            information = json.dumps(user_data)
            information2 = json.loads(information)
            return information2, information
    return None, None

def get_user_addresses(email):
    addresses = []
    existing_addresses = addresses_ref.where('email', '==', email).get()
    if existing_addresses:
        for address in existing_addresses:
            address_doc = addresses_ref.document(address.id).get().to_dict()
            addresses.append(address_doc)
    addresses_dict = json.dumps(addresses)
    return addresses, addresses_dict


@csrf_exempt
@login_required
def update_user_account(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            old_data = data.get('old')
            new_data = data.get('new')

            old_email = old_data['email']
            new_email = new_data['email']

            # Check for existing user by email
            existing_users = users_ref.where('email', '==', old_email).limit(1).get()
            if new_data['firstname'] != old_data['first_name'] or new_data['lastname'] != old_data['last_name']:
                User = get_user_model()
                try:
                    user_instance = User.objects.get(email=old_email)
                    user_instance.first_name = new_data['firstname']
                    user_instance.last_name = new_data['lastname']
                    user_instance.save()
                except User.DoesNotExist:
                    return JsonResponse({'status': 'error', 'message': 'User not found.'}, status=404)

            if new_data['email'] != old_email:
                existing_user_with_new_email = users_ref.where('email', '==', new_email).limit(1).get()
                if len(existing_user_with_new_email) > 0:
                    return JsonResponse({'status': 'error', 'message': 'User with this email exists.'}, status=400)
                User = get_user_model()
                try:
                    user_instance = User.objects.get(email=old_email)
                    user_instance.email = new_email  # Update the email
                    user_instance.username = new_email  # Update the email
                    user_instance.save()
                except User.DoesNotExist:
                    return JsonResponse({'status': 'error', 'message': 'User not found.'}, status=404)

                try:
                    update_email_in_db(old_email, new_email)
                    # Optionally use update_email_in_db_result for further logic
                except Exception as e:
                    # Log the exception e
                    return JsonResponse(
                        {'status': 'error', 'message': 'An error occurred while updating documents in Firestore.'},
                        status=500)
            else:
                User = get_user_model()
                try:
                    # Retrieve the user instance
                    user_instance = User.objects.get(email=old_email)
                except User.DoesNotExist:
                    return JsonResponse({'status': 'error', 'message': 'User not found.'}, status=404)

            social_title = old_data['social_title'] if 'id_gender' not in new_data else "Mr" if new_data[
                                                                                                    'id_gender'] == "1" else "Mrs"
            receive_newsletter = old_data['receive_newsletter'] if 'newsletter' not in new_data else True if new_data[
                                                                                                                 'newsletter'] == "1" else False
            receive_offers = old_data['receive_offers'] if 'optin' not in new_data else True if new_data[
                                                                                                    'optin'] == "1" else False
            password = new_data['password']

            # Check if the provided password matches the user's password
            if not user_instance.check_password(password):
                return JsonResponse({'status': 'error', 'message': 'Incorrect password.'}, status=400)

            new_password = new_data.get('new_password', '')
            if new_password:  # This checks if the new_password string is not empty
                user_instance.set_password(new_password)
                user_instance.save()  # Don't forget to save the user object after setting the new password
                update_session_auth_hash(request, user_instance)

            user_instance.save()

            for user in existing_users:
                user_ref = users_ref.document(user.id)
                user_ref.update({
                    'social_title': social_title,
                    'first_name': new_data['firstname'],
                    'last_name': new_data['lastname'],
                    'email': new_data['email'],
                    'birthday': new_data['birthday'],
                    'receive_newsletter': receive_newsletter,
                    'receive_offers': receive_offers,
                })
                return JsonResponse({'status': 'success', 'message': 'User updated successfully.'})

            return JsonResponse({'status': 'success', 'message': 'User account updated successfully.'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=400)


def upload_file(request):
    if request.method == 'POST' and 'file' in request.FILES:
        uploaded_file = request.FILES['file']

        # Проверка на корректное расширение файла
        if not (uploaded_file.name.endswith('.xlsx') or uploaded_file.name.endswith('.xls')):
            return JsonResponse({'status': 'error', 'message': 'Invalid file format. Only .xlsx or .xls are allowed'}, status=400)

        try:
            # Открываем загруженный файл с помощью openpyxl
            workbook = load_workbook(uploaded_file)
            sheet = workbook.active

            # Проходим по строкам файла и вызываем нужную функцию
            for row in sheet.iter_rows(min_row=2, values_only=True):  # min_row=2 пропускает заголовок
                product_name, new_quantity = row
                if not product_name or new_quantity is None:
                    continue  # Пропускаем строки с отсутствующими данными

                product_name = str(product_name)
                new_quantity = int(new_quantity)
                # Получаем данные из пользовательской сессии и вызываем нужные функции
                email = get_user_session_type(request)
                category, currency = get_user_prices(request, email)
                currency = '€' if currency == 'Euro' else '$'
                info = get_user_info(email) or {}
                sale = round((0 if "sale" not in info else info['sale'])/100, 3) or 0

                # Проверяем наличие имени товара и количества
                if not product_name or new_quantity is None:
                    continue  # Пропускаем строки без продукта или количества

                # Ищем информацию о продукте
                document = get_full_product(product_name)
                if not document:
                    continue  # Если продукт не найден, продолжаем обработку следующей строки

                # Определяем цену товара в зависимости от категории
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

                # Обновляем корзину
                subtotal, cart_size = update_cart(email, product_name, new_quantity, document)

                if subtotal is None:
                    return JsonResponse({'status': 'error', 'message': 'An error occurred while processing your request'}, status=500)

            return JsonResponse({'status': 'success', 'message': 'All products processed successfully'})

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': f'Error processing file: {str(e)}'}, status=500)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)