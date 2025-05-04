from django.conf import settings
from django.shortcuts import render


def service_pages_view(request, service_page):
    """
    View page for service pages. This view is used to render the service pages. It takes in the service page as a parameter and renders the corresponding template.
    :param request:
    :param service_page:
    :return:
    """
    context = {"service_page": service_page}
    if service_page == 'stores':
        context['GOOGLE_MAPS_API_KEY'] = settings.GOOGLE_MAPS_API_KEY
    return render(request, 'service_pages/main_service_template.html', context)

