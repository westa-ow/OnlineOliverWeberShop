from django.shortcuts import redirect
from django.urls import reverse


class EnsureAnonymousSessionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # The code executed on each request before the view
        response = self.get_response(request)
        # Code executed on each response after the view
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        # Check: if it's a Stripe webhook, we don't perform the redirection
        webhook_paths = [
            reverse('stripe_webhook'),  # Make sure the path matches your webhook route
            reverse('product_feed'),
        ]

        if request.path in webhook_paths:
            # If it's a webhook request, don't do a redirect
            return None

        # Check if the user has a session key
        if not request.user.is_authenticated and not request.session.session_key:
            # Generate session key
            request.session.save()
            # Check if we are already on the home page to avoid endless redirects
            if request.path != reverse('home'):
                return redirect('home')

        return None