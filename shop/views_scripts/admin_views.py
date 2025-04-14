import concurrent

from django.contrib.auth.decorators import login_required

from shop.tasks import process_file_task
from shop.views import db, orders_ref, serialize_firestore_document, itemsRef, get_cart, cart_ref, single_order_ref, \
    is_admin, users_ref, metadata_ref, get_user_prices
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


@user_passes_test(is_admin)
def upload_view(request):
    message = ""
    if request.method == "POST":
        if 'file' not in request.FILES:
            message = "File is missing!"
        else:
            file = request.FILES['file']
            try:
                save_dir = os.path.join(settings.BASE_DIR, 'storages')
                os.makedirs(save_dir, exist_ok=True)
                save_path = os.path.join(save_dir, file.name)
                with open(save_path, 'wb+') as destination:
                    for chunk in file.chunks():
                        destination.write(chunk)
                process_file_task(save_path)
                message = "File processing started!"
            except Exception as e:
                message = f"An error occurred: {str(e)}"
    return render(request, 'admin_tools/AT_upload_db_update.html', {"message": message})