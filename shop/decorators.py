from django.http import HttpResponseForbidden
from functools import wraps

def login_required_or_session(f):
    @wraps(f)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated or request.session.session_key:
            return f(request, *args, **kwargs)
        else:
            return HttpResponseForbidden("Доступ запрещен")
    return wrapper