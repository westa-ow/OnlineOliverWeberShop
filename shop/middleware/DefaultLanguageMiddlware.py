from django.utils import translation
from django.conf import settings
from django.shortcuts import redirect
import re

class DefaultLanguageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # If the language is not set, force set 'gb'
        if not re.match(r'^/(gb|de|it|fr|es|ru)/', request.path):
            # Redirect to gb only if the language is not set in the URL
            return redirect(f'/gb{request.path}')
        response = self.get_response(request)
        return response
