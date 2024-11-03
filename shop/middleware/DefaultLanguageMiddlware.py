from django.utils import translation
from django.conf import settings
from django.shortcuts import redirect


class DefaultLanguageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Если язык не установлен, принудительно установить 'gb'
        if not request.path.startswith(f'/{settings.LANGUAGE_CODE}/'):
            return redirect(f'/{settings.LANGUAGE_CODE}/')
        response = self.get_response(request)
        return response
