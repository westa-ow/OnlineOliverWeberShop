from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.files.storage import default_storage
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string

from shop.forms import EditBannerForm
from shop.models import Banner, BannerLanguage
from shop.views import is_admin


@login_required
@user_passes_test(is_admin)
def delete_banner_relationship(request, rel_id):
    if request.method == "POST":
        try:
            banner_lang = BannerLanguage.objects.get(id=rel_id)
        except BannerLanguage.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Banner relationship not found.'}, status=404)

        banner = banner_lang.banner
        current_language = banner_lang.language.code

        rel_count = BannerLanguage.objects.filter(banner=banner).count()

        if rel_count > 1:
            # Delete only the link for the current language
            banner_lang.delete()
            message = "Banner removed for current language."
        else:
            # If the link is the only one, you can either perform a complete removal,
            # or notify them that the banner is being removed completely.
            # Here we suggest a complete removal.
            if banner.image:
                image_path = banner.image.path
                if default_storage.exists(image_path):
                    default_storage.delete(image_path)
            banner.delete()
            message = "Banner fully deleted."

        remaining_rels = BannerLanguage.objects.filter(language__code=current_language, banner__active=True).order_by(
            'priority')
        for index, rel in enumerate(remaining_rels):
            rel.priority = index
            rel.save()

        return JsonResponse({'status': 'ok', 'message': message})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)

@login_required
@user_passes_test(is_admin)
def delete_banner_all(request, banner_id):
    if request.method == "POST":
        try:
            banner = Banner.objects.get(id=banner_id)
        except Banner.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Banner not found.'}, status=404)

        # If the banner has an image, delete the file
        if banner.image:
            image_path = banner.image.path
            if default_storage.exists(image_path):
                default_storage.delete(image_path)

        # Completely remove the banner; thanks to Django's cascading removal, related entries in BannerLanguage will also be removed,
        # or you can delete them explicitly if you want
        banner.delete()

        # If necessary, you can reorder banners for each language, but more often a page refresh is sufficient
        return JsonResponse({'status': 'ok', 'message': 'Banner fully deleted.'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)


@login_required
@user_passes_test(is_admin)
def edit_banner(request, banner_id):
    banner = get_object_or_404(Banner, id=banner_id)
    if request.method == "POST":
        form = EditBannerForm(request.POST, instance=banner)
        if form.is_valid():
            form.save()
            return JsonResponse({'status': 'ok', 'message': 'Banner updated successfully'})
        else:
            html = render_to_string('admin_tools/widgets/edit_banner_form.html', {'form': form, 'banner': banner}, request=request)
            return JsonResponse({'status': 'error', 'html': html})
    else:
        form = EditBannerForm(instance=banner)
        html = render_to_string('admin_tools/widgets/edit_banner_form.html', {'form': form, 'banner': banner}, request=request)
        return JsonResponse({'status': 'ok', 'html': html})


@login_required
@user_passes_test(is_admin)
def move_up(request, banner_id):
    language_code = request.POST.get('lang')
    try:
        # Find an object in the intermediate model for the banner and the specified language
        banner_lang = BannerLanguage.objects.get(banner_id=banner_id, language__code=language_code)
    except BannerLanguage.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Banner for this language was not found.'}, status=404)

    # Look for the previous banner in order for the same language
    previous_banner = BannerLanguage.objects.filter(
        language__code=language_code,
        priority__lt=banner_lang.priority
    ).order_by('-priority').first()

    if previous_banner:
        banner_lang.priority, previous_banner.priority = previous_banner.priority, banner_lang.priority
        banner_lang.save()
        previous_banner.save()
        return JsonResponse({'success': True})
    else:
        return JsonResponse({'success': False, 'error': 'There is no banner above for this language.'})

@login_required
@user_passes_test(is_admin)
def move_down(request, banner_id):
    language_code = request.POST.get('lang')
    try:
        banner_lang = BannerLanguage.objects.get(banner_id=banner_id, language__code=language_code)
    except BannerLanguage.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Banner for this language was not found.'}, status=404)

    # Looking for the next banner in order
    next_banner = BannerLanguage.objects.filter(
        language__code=language_code,
        priority__gt=banner_lang.priority
    ).order_by('priority').first()

    if next_banner:
        banner_lang.priority, next_banner.priority = next_banner.priority, banner_lang.priority
        banner_lang.save()
        next_banner.save()
        return JsonResponse({'success': True})
    else:
        return JsonResponse({'success': False, 'error': 'There is no banner below for this language.'})