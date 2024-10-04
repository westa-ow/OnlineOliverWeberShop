from shop.views import get_user_info


def user_role(request):
    role = None
    if request.user.is_authenticated:
        user_info = get_user_info(request.user.email)
        role = user_info['role'] if user_info and 'role' in user_info else None
    return {'user_role': role}