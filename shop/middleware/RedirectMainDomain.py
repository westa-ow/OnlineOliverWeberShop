from django.http import HttpResponsePermanentRedirect

class WWWRedirectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.get_host()

        # Перенаправление с oliverweber.com на www.oliverweber.com
        if host == 'oliverweber.com':
            return HttpResponsePermanentRedirect(f'https://www.oliverweber.com{request.get_full_path()}')

        # Продолжаем обработку запроса
        return self.get_response(request)
