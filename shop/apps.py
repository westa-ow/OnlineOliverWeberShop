from django.apps import AppConfig


class ShopConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'shop'

    def ready(self):
        # Импортируем модуль сигналов, чтобы зарегистрировать обработчик
        import shop.axes_signals
