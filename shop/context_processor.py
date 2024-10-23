from shop.views import get_user_info


def user_role(request):
    role = None
    if request.user.is_authenticated:
        user_info = get_user_info(request.user.email)
        role = user_info['role'] if user_info and 'role' in user_info else None
    return {'user_role': role}

def user_is_special(request):
    special = False
    if request.user.is_authenticated:
        user_info = get_user_info(request.user.email)
        special = user_info['special_customer'] if user_info and 'special_customer' in user_info else False
    return {'isSpecialCustomer': special}

def customer_type(request):
    type = None
    if request.user.is_authenticated:
        user_info = get_user_info(request.user.email)
        type = user_info['customer_type'] if user_info and 'customer_type' in user_info else "Customer"
    return {'customer_type': type}