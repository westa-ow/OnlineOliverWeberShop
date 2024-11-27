from django.urls import reverse

from shop.views import get_user_info


def user_role(request):
    role = None
    if request.user.is_authenticated:
        user_info = get_user_info(request.user.email)
        role = user_info['role'] if user_info and 'role' in user_info else "Customer"
    return {'user_role': role}

def user_is_special(request):
    special = False
    if request.user.is_authenticated:
        user_info = get_user_info(request.user.email)
        special = user_info['special_customer'] if user_info and 'special_customer' in user_info else False
    return {'isSpecialCustomer': special}

def customer_type(request):
    type = "Customer"
    if request.user.is_authenticated:
        user_info = get_user_info(request.user.email)
        type = user_info['customer_type'] if user_info and 'customer_type' in user_info else "Customer"
    return {'customer_type': type}


def shop_page_url(request):
    """
    Контекстный процессор для добавления полного URL для shop_page.
    """
    if request.resolver_match:  # Убедимся, что request содержит информацию о маршруте
        full_url = request.build_absolute_uri(
            reverse('shop_page', kwargs={'product_id': 'REPLACE'})
        )
    else:
        full_url = None

    return {'shop_page_url': full_url}