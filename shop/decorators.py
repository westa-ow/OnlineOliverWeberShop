from django.http import HttpResponseForbidden, HttpResponseRedirect
from functools import wraps

from django.urls import reverse


def login_required_or_session(f):
    @wraps(f)
    def wrapper(request, *args, **kwargs):
        # Check if the user is authenticated
        if request.user.is_authenticated:
            return f(request, *args, **kwargs)
        # If not authenticated, check for a session key
        elif not request.session.session_key:
            # No session exists, so create one
            request.session.save()  # This ensures a session is created
        # Now, there must be a session key after the above save
        if request.session.session_key:
            return f(request, *args, **kwargs)
        else:
            return HttpResponseForbidden("Access denied")
    return wrapper

def logout_required(function):
    def wrap(request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse('checkout_addresses'))  # Redirect to a named URL 'home'
        else:
            return function(request, *args, **kwargs)
    return wrap