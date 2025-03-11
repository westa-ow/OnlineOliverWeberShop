import ast
import random
from datetime import datetime
from random import randint
import geoip2.database

import concurrent.futures

import stripe
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
from rest_framework import viewsets, status
from rest_framework.response import Response

from OnlineShop.settings import GEOIP_PATH, GEOIP_config
from shop.forms import UserRegisterForm, User, BannerForm
from django.utils.translation import gettext as _

from shop.models import Banner, PromoCode
from shop.views_scripts.serializers import PromoCodeSerializer


class PromoCodeViewSet(viewsets.ViewSet):
    def list(self, request):
        # Get a list of all promo codes
        promocodes = PromoCode.get_all()
        return Response(promocodes)

    def retrieve(self, request, pk=None):
        # Get one promo code by ID
        promocode = PromoCode.get_by_id(pk)
        if not promocode:
            return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
        return Response(promocode)

    def create(self, request):
        # Create new promo code
        serializer = PromoCodeSerializer(data=request.data)
        if serializer.is_valid():
            doc_id = PromoCode.create(serializer.validated_data)
            return Response({'id': doc_id}, status=status.HTTP_201_CREATED)
        else:
            print("Validation errors:", serializer.errors)  # Лог ошибок валидации
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        # Update promo code
        serializer = PromoCodeSerializer(data=request.data)
        if serializer.is_valid():
            PromoCode.update(pk, serializer.validated_data)
            return Response({'status': 'updated'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        # Delete promo code
        PromoCode.delete(pk)
        return Response({'status': 'deleted'}, status=status.HTTP_204_NO_CONTENT)