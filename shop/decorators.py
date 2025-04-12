from django.http import HttpResponseForbidden, HttpResponseRedirect, JsonResponse, HttpResponse
from functools import wraps

from django.shortcuts import redirect
from django.urls import reverse
from django_ratelimit.decorators import ratelimit


def login_required_or_session(f):
    @wraps(f)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated or request.session.session_key:
            return f(request, *args, **kwargs)
        else:
            return JsonResponse({'status': 'error', 'message': 'Access denied'}, status=403)
    return wrapper


def logout_required(function):
    def wrap(request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse('checkout_addresses'))  # Redirect to a named URL 'home'
        else:
            return function(request, *args, **kwargs)
    return wrap


def not_logged_in(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def ratelimit_with_logging(key, rate, block=False, **kwargs):
    def decorator(fn):
        @ratelimit(key=key, rate=rate, block=False, **kwargs)
        def wrapper(request, *args, **inner_kwargs):
            if getattr(request, 'limited', False):
                import logging
                logger = logging.getLogger(__name__)
                logger.warning("Rate limit exceeded for IP: %s", request.META.get('REMOTE_ADDR'))
                # We return code 429 - Too Many Requests
                return HttpResponse("Too Many Requests", status=429)
            return fn(request, *args, **inner_kwargs)
        return wrapper
    return decorator
