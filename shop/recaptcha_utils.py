import requests
from django.conf import settings

def verify_recaptcha(recaptcha_response):
    secret_key = settings.RECAPTCHA_SECRET_KEY
    data = {
        'secret': secret_key,
        'response': recaptcha_response
    }
    r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
    result = r.json()
    return result.get('success', False)
