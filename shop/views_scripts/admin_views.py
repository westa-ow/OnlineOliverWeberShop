import os

from django.conf import settings
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render

from shop.tasks import process_file_task
from shop.views import is_admin


@user_passes_test(is_admin)
def upload_view(request):
    message = ""
    if request.method == "POST":
        if 'file' not in request.FILES:
            message = "File is missing!"
        else:
            file = request.FILES['file']
            try:
                save_dir = os.path.join(settings.BASE_DIR, 'storages')
                os.makedirs(save_dir, exist_ok=True)
                save_path = os.path.join(save_dir, file.name)
                with open(save_path, 'wb+') as destination:
                    for chunk in file.chunks():
                        destination.write(chunk)
                process_file_task(save_path)
                message = "File processing started!"
            except Exception as e:
                message = f"An error occurred: {str(e)}"
    return render(request, 'admin_tools/AT_upload_db_update.html', {"message": message})