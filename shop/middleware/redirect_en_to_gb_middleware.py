from django.shortcuts import redirect

class RedirectENtoGBMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if the URL starts with /en/
        if request.path.startswith('/en/'):
            # Forming a new URL
            new_path = request.path.replace('/en/', '/gb/', 1)
            return redirect(new_path)
        return self.get_response(request)