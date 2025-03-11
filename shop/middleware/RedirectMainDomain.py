from django.http import HttpResponsePermanentRedirect

class WWWRedirectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.get_host()

        # Redirects from oliverweber.com to www.oliverweber.com
        if host == 'oliverweber.com':
            return HttpResponsePermanentRedirect(f'https://www.oliverweber.com{request.get_full_path()}')

        # Continue processing the request
        return self.get_response(request)
