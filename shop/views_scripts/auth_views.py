import logging
import time
from datetime import datetime

from axes.models import AccessAttempt
from axes.utils import reset
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import PasswordResetConfirmView
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from firebase_admin import firestore

from shop.decorators import ratelimit_with_logging, not_logged_in
from shop.forms import UserRegisterForm, User
from shop.recaptcha_utils import verify_recaptcha
from shop.views import db, users_ref, metadata_ref, get_user_prices

logger = logging.getLogger(__name__)


def get_new_user_id():
    @firestore.transactional
    def increment_user_id(transaction, user_counter_ref):
        snapshot = user_counter_ref.get(transaction=transaction)
        last_user_id = snapshot.get('lastUserId') if snapshot.exists else 3000
        incremented_user_id = last_user_id + 1
        transaction.update(user_counter_ref, {'lastUserId': incremented_user_id})
        return incremented_user_id

    user_counter_ref = metadata_ref.document('userCounter')
    transaction = db.transaction()
    new_user_id = increment_user_id(transaction, user_counter_ref)
    return new_user_id


@not_logged_in
@ratelimit_with_logging(key='ip', rate='5/m', block=True)
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)

        recaptcha_response = request.POST.get('g-recaptcha-response')
        if not verify_recaptcha(recaptcha_response):
            form.add_error(None, 'Invalid reCAPTCHA. Please try again.')
            logger.error("Registration failed: invalid reCAPTCHA. Errors: %s", form.errors.as_json())
            return render(request, 'registration/register.html', {
                'form': form,
                'errors': form.errors,
                'error_messages': get_all_errors(form),
                'RECAPTCHA_SITE_KEY': settings.RECAPTCHA_SITE_KEY
            })

        if form.is_valid():
            email = form.cleaned_data.get('email')
            existing_user = users_ref.where('email', '==', email).limit(1).get()

            if list(existing_user):  # Convert to list to check if it's non-empty
                error_message = 'User with this Email already exists.'
                form.add_error('email', error_message)
                logger.error("Registration failed: %s. Email: %s", error_message, email)
                return render(request, 'registration/register.html', {
                   "form": form,
                   "errors": form.errors,
                   "error_messages": get_all_errors(form),
                   "RECAPTCHA_SITE_KEY": settings.RECAPTCHA_SITE_KEY
                })

            user_id = get_new_user_id()
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')
            birthdate = form.cleaned_data.get('birthdate')
            social_title = "Mr" if form.cleaned_data.get('social_title') == "1" else "Mrs"
            customer_type = "Customer"
            offers = form.cleaned_data.get('offers')
            newsletter = form.cleaned_data.get('receive_newsletter')
            category, currency = get_user_prices(request, email)
            new_user = {
                'Enabled': True,
                "display_name": "undefined",
                'social_title': social_title,
                'first_name': first_name,
                'last_name': last_name,
                'email': email,
                'birthday': birthdate,
                'country': "",
                "agent_number": "",
                'price_category': category,
                'currency': currency,
                'receive_offers': offers,
                'receive_newsletter': newsletter,
                'registrationDate': current_time,
                'userId': user_id,
                'sale': 0,
                'customer_type': customer_type,
                'show_quantities': False
            }
            users_ref.add(new_user)

            username = email
            unique_suffix = 1
            original_username = username
            while User.objects.filter(username=username).exists():
                username = f"{original_username}{unique_suffix}"
                unique_suffix += 1
            user = form.save(commit=False)
            user.username = username  # Set the unique username
            user.save()  # Now save the user to the database

            password = form.cleaned_data.get('password1')
            form.save()
            user = authenticate(request=request, username=username, password=password)
            if user:
                login(request, user)
                logger.info("User registered successfully: %s", email)
                return redirect('home')
        else:
            logger.error("Registration form validation errors: %s", form.errors.as_json())
            return render(request, 'registration/register.html', {
                'form': form,
                'errors': form.errors,
                'error_messages': get_all_errors(form),
                'RECAPTCHA_SITE_KEY': settings.RECAPTCHA_SITE_KEY
            })
    else:
        form = UserRegisterForm()

    print(form.errors)
    return render(request, 'registration/register.html', {'form': form, 'errors': form.errors, 'RECAPTCHA_SITE_KEY': settings.RECAPTCHA_SITE_KEY, 'error_messages': get_all_errors(form)})


@not_logged_in
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, request.POST)

        locked_until = request.session.get('axes_locked_until')
        if locked_until:
            current_time = time.time()  # Current time in seconds
            if current_time < locked_until:
                unlock_time = datetime.fromtimestamp(locked_until)
                error_msg = f"Your account is locked due to too many failed login attempts. Please try again after {unlock_time.strftime('%H:%M:%S')}."
                form.add_error(None, error_msg)
                return render(request, 'registration/login.html', {'form': form, 'error_messages': get_all_errors(form)})
            else:
                # If the blocking period has expired, clear the flag
                request.session.pop('axes_locked_until', None)

        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request=request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
        # If the form is not valid, proceed to rendering the login page with errors
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form, 'error_messages': get_all_errors(form)})


def get_all_errors(forms):
    # If list is passed - just continue. If it is not list - we should wrap it inside of the new list
    if not isinstance(forms, list):
        forms = [forms]
    seen = set()
    all_errors = []
    for form in forms:
        for field, errors in form.errors.items():
            for error in errors:
                message = f"{field}: {error}" if field != "__all__" else error
                if message not in seen:
                    seen.add(message)
                    all_errors.append(message)
        # Process non-field errors separately
        for error in form.non_field_errors():
            if error not in seen:
                seen.add(error)
                all_errors.append(error)
    return all_errors


def logout_view(request):
    logout(request)
    return redirect('home')


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'registration/password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete')

    def get_user(self, uidb64=None):
        # If uidb64 is not passed, we take it from self.kwargs
        if uidb64 is None:
            uidb64 = self.kwargs.get('uidb64')
        # Call parent implementation with passed uidb64
        return super().get_user(uidb64)

    def form_valid(self, form):
        # If the password reset is successful, save the user
        response = super().form_valid(form)
        # Retrieve the user after changing the password.
        user = self.get_user()
        if user:
            try:
                # Remove records of failed attempts from the axes_accessattempt table for this user
                reset(user.username)
                AccessAttempt.objects.filter(username=user.username).delete()
                logger.info("Axes access attempts cleared for user: %s", user.username)
                if 'axes_locked' in self.request.session:
                    logger.info("Deleted axes locked flag")
                    del self.request.session['axes_locked']
                if 'axes_locked_until' in self.request.session:
                    logger.info("Deleted axes locked until flag")
                    del self.request.session['axes_locked_until']
                self.request.session.modified = True
            except Exception as e:
                logger.error("Error clearing axes attempts for user %s: %s", user.username, e)
        return response


def lockout_view(request):
    unlock_timestamp = request.session.get("axes_locked_until")
    unlock_datetime = None

    if not unlock_timestamp or time.time() >= unlock_timestamp:
        return redirect(reverse('login'))

    if unlock_timestamp:
        unlock_datetime = datetime.fromtimestamp(unlock_timestamp)

    return render(request, 'registration/lockout.html', {
        'unlock_time': unlock_datetime.strftime('%H:%M') if unlock_datetime else None,
    })
