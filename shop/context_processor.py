from django.urls import reverse

from shop.views import get_user_info, get_vocabulary_product_card


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


def b2b_can_pay(request):
    can_b2b_pay = False
    if request.user.is_authenticated:
        user_info = get_user_info(request.user.email)
        if user_info and 'customer_type' in user_info:
            if user_info['customer_type'] == 'B2B':
                can_b2b_pay = user_info.get('b2b_can_pay', False)
    return {'b2b_can_pay': can_b2b_pay}


def shop_page_url(request):
    """
    Context processor to add the full URL for shop_page.
    """
    if request.resolver_match:  # Let's make sure that the request contains route information
        full_url = request.build_absolute_uri(
            reverse('shop_page', kwargs={'product_id': 'REPLACE'})
        )
    else:
        full_url = None

    return {'shop_page_url': full_url}


def hotjar(request):
    from django.conf import settings
    return {'USE_HOTJAR': getattr(settings, 'USE_HOTJAR', False)}

def hotjar_id(request):
    from django.conf import settings

    return {'HOTJAR_ID': getattr(settings, 'HOTJAR_ID', '')}


def vocabulary_translation(request):
    return {'vocabulary': get_vocabulary_product_card()}