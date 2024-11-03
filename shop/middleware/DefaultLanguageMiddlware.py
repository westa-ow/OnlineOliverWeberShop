from django.utils import translation
from django.conf import settings
from django.shortcuts import redirect
import re

class DefaultLanguageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Если язык не установлен, принудительно установить 'gb'
        if not re.match(r'^/(gb|de|it|fr|es|ru)/', request.path):
            # Перенаправляем на gb только если язык не установлен в URL
            return redirect(f'/gb{request.path}')
        response = self.get_response(request)
        return response
