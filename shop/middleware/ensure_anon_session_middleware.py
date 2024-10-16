from django.shortcuts import redirect
from django.urls import reverse


class EnsureAnonymousSessionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Код, выполняемый на каждый запрос перед view
        response = self.get_response(request)
        # Код, выполняемый на каждый ответ после view
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        # Проверка: если это вебхук Stripe, мы не выполняем перенаправление
        webhook_paths = [
            reverse('stripe_webhook'),  # Убедитесь, что путь совпадает с вашим маршрутом вебхука
        ]

        if request.path in webhook_paths:
            # Если это запрос на вебхук, не делаем перенаправление
            return None

        # Проверяем, есть ли у пользователя сессионный ключ
        if not request.user.is_authenticated and not request.session.session_key:
            # Генерируем сессионный ключ
            request.session.save()
            # Проверяем, не находимся ли мы уже на главной странице, чтобы избежать бесконечного редиректа
            if request.path != reverse('home'):
                return redirect('home')

        return None