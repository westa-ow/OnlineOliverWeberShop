import ast
import random
from datetime import datetime
from random import randint
import geoip2.database

import concurrent.futures
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_user_model, update_session_auth_hash
import os
import json
import firebase_admin
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from firebase_admin import credentials, firestore
from django.conf import settings
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.mail import send_mail

from shop.forms import UserRegisterForm, User, BannerForm, EditBannerForm
from django.utils.translation import gettext as _

from shop.models import Banner, BannerLanguage
from shop.views import is_admin
from django.core.files.storage import default_storage


@login_required
@user_passes_test(is_admin)
def delete_banner_relationship(request, rel_id):
    if request.method == "POST":
        try:
            banner_lang = BannerLanguage.objects.get(id=rel_id)
        except BannerLanguage.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Banner relationship not found.'}, status=404)

        # Получаем баннер и язык текущей записи
        banner = banner_lang.banner
        current_language = banner_lang.language.code

        # Считаем количество связей для данного баннера
        rel_count = BannerLanguage.objects.filter(banner=banner).count()

        if rel_count > 1:
            # Удаляем только связь для текущего языка
            banner_lang.delete()
            message = "Banner removed for current language."
        else:
            # Если связь единственная, можно либо выполнить полное удаление,
            # либо уведомить, что баннер удаляется полностью.
            # Здесь предлагаем полное удаление.
            if banner.image:
                image_path = banner.image.path
                if default_storage.exists(image_path):
                    default_storage.delete(image_path)
            banner.delete()
            message = "Banner fully deleted."

        # Переупорядочиваем оставшиеся связи для данного языка
        remaining_rels = BannerLanguage.objects.filter(language__code=current_language, banner__active=True).order_by(
            'priority')
        for index, rel in enumerate(remaining_rels):
            rel.priority = index
            rel.save()

        return JsonResponse({'status': 'ok', 'message': message})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)

@login_required
@user_passes_test(is_admin)
def delete_banner_all(request, banner_id):
    if request.method == "POST":
        try:
            banner = Banner.objects.get(id=banner_id)
        except Banner.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Banner not found.'}, status=404)

        # Если баннер имеет изображение, удаляем файл
        if banner.image:
            image_path = banner.image.path
            if default_storage.exists(image_path):
                default_storage.delete(image_path)

        # Полностью удаляем баннер; благодаря каскадному удалению Django связанные записи в BannerLanguage также будут удалены,
        # либо можно удалить их явно, если требуется
        banner.delete()

        # При необходимости можно выполнить переупорядочивание баннеров для каждого языка, но чаще обновление страницы достаточно
        return JsonResponse({'status': 'ok', 'message': 'Banner fully deleted.'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)


@login_required
@user_passes_test(is_admin)
def edit_banner(request, banner_id):
    banner = get_object_or_404(Banner, id=banner_id)
    if request.method == "POST":
        form = EditBannerForm(request.POST, instance=banner)
        if form.is_valid():
            form.save()
            return JsonResponse({'status': 'ok', 'message': 'Banner updated successfully'})
        else:
            html = render_to_string('admin_tools/widgets/edit_banner_form.html', {'form': form, 'banner': banner}, request=request)
            return JsonResponse({'status': 'error', 'html': html})
    else:
        form = EditBannerForm(instance=banner)
        html = render_to_string('admin_tools/widgets/edit_banner_form.html', {'form': form, 'banner': banner}, request=request)
        return JsonResponse({'status': 'ok', 'html': html})


@login_required
@user_passes_test(is_admin)
def move_up(request, banner_id):
    language_code = request.POST.get('lang')
    try:
        # Находим объект в промежуточной модели для баннера и заданного языка
        banner_lang = BannerLanguage.objects.get(banner_id=banner_id, language__code=language_code)
    except BannerLanguage.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Banner для данного языка не найден.'}, status=404)

    # Ищем предыдущий баннер по порядку для этого же языка
    previous_banner = BannerLanguage.objects.filter(
        language__code=language_code,
        priority__lt=banner_lang.priority
    ).order_by('-priority').first()

    if previous_banner:
        banner_lang.priority, previous_banner.priority = previous_banner.priority, banner_lang.priority
        banner_lang.save()
        previous_banner.save()
        return JsonResponse({'success': True})
    else:
        return JsonResponse({'success': False, 'error': 'Нет баннера выше для этого языка.'})

@login_required
@user_passes_test(is_admin)
def move_down(request, banner_id):
    language_code = request.POST.get('lang')
    try:
        banner_lang = BannerLanguage.objects.get(banner_id=banner_id, language__code=language_code)
    except BannerLanguage.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Banner для данного языка не найден.'}, status=404)

    # Ищем следующий баннер по порядку
    next_banner = BannerLanguage.objects.filter(
        language__code=language_code,
        priority__gt=banner_lang.priority
    ).order_by('priority').first()

    if next_banner:
        banner_lang.priority, next_banner.priority = next_banner.priority, banner_lang.priority
        banner_lang.save()
        next_banner.save()
        return JsonResponse({'success': True})
    else:
        return JsonResponse({'success': False, 'error': 'Нет баннера ниже для этого языка.'})