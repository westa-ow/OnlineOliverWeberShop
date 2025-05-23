import json

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.shortcuts import render

from shop.views import users_ref, is_admin, update_email_in_db, currency_dict, groups_dict, \
    serialize_firestore_document, get_user_prices


@login_required
@user_passes_test(is_admin)
def edit_user(request, user_id):
    print("Edit user " + user_id)
    email = request.user.email
    category, currency = get_user_prices(request, email)
    currency = '€' if currency == 'Euro' else '$'
    existing_user = users_ref.where('userId', '==', int(user_id)).limit(1).stream()
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            old_user_data = json.loads(data.get('old'))
            new_user_data = data.get('new')

            old_email = old_user_data['email']
            new_email = new_user_data['email']
            new_password = new_user_data.get('password')  # Getting a new password


            if new_email != old_email:
                existing_user_with_new_email = users_ref.where('email', '==', new_email).limit(1).get()
                if len(existing_user_with_new_email) > 0:
                    return JsonResponse({'status': 'error', 'message': 'User with this email exists.'}, status=400)

            User = get_user_model()
            try:
                user_instance = User.objects.get(email=old_email)

                # Update email if it has changed
                if new_email != old_email:
                    user_instance.username = new_email
                    user_instance.email = new_email
                    try:
                        update_email_in_db(old_email, new_email)
                    except Exception as e:
                        # Log the exception e
                        return JsonResponse(
                            {'status': 'error', 'message': 'An error occurred while updating documents in Firestore.'},
                            status=500)

                # Update the password, if provided
                if new_password:  # This checks if the new_password string is not empty
                    try:
                        # Check the new password before setting it
                        validate_password(new_password, user_instance)
                        user_instance.set_password(new_password)
                        user_instance.save()  # Don't forget to save the user object after setting the new password

                    except ValidationError as e:
                        # Return an error if the password failed validation
                        return JsonResponse({'status': 'error', 'message': list(e.messages)}, status=400)



                user_instance.save()  # Save the changes in the database

            except User.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'User not found.'}, status=404)

            social_title = old_user_data['social_title'] if 'id_gender' not in new_user_data else "Mr" if new_user_data[
                                                                                                    'id_gender'] == "1" else "Mrs"
            receive_offers = False if 'receive-partners-offers' not in new_user_data else True if new_user_data[
                                                                                                 'receive-partners-offers'] == "1" else False
            user_enabled = False if 'enable-user' not in new_user_data else True if new_user_data[
                                                                                                              'enable-user'] == "1" else False
            show_quantities = False if 'show-quantities' not in new_user_data else True if new_user_data[
                                                                                                              'show-quantities'] == "1" else False
            customer_type = "Customer" if 'is-b2b' not in new_user_data else "B2B" if new_user_data[
                                                                                               'is-b2b'] == "1" else "Customer"
            can_b2b_pay = False if 'can-b2b' not in new_user_data else True if new_user_data[
                                                                                          'is-b2b'] == "1" else False

            customer_currency = currency_dict[new_user_data['id_currency']]
            customer_group = groups_dict[new_user_data['id_group']]
            if customer_group != "Default" and customer_group != "Default_USD":
                del new_user_data['sale']
            if existing_user:
                for user in existing_user:
                    user_ref = users_ref.document(user.id)
                    user_ref.update({
                        'Enabled': user_enabled,
                        'social_title': social_title,
                        'first_name': new_user_data['firstname'],
                        'last_name': new_user_data['lastname'],
                        'email': new_user_data['email'],
                        'birthday': new_user_data['birthday'],
                        'agent_number': new_user_data['client-name'],
                        'currency': customer_currency,
                        'receive_offers': receive_offers,
                        'sale': 0 if "sale" not in new_user_data else float(new_user_data['sale']),
                        'price_category': customer_group,
                        'show_quantities': show_quantities,
                        'customer_type': customer_type,
                        'b2b_can_pay': can_b2b_pay,
                    })
            return JsonResponse({'status': 'success', 'message': 'Address updated successfully.'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    context = {
        'feature_name': "edit_user",
        'currency': currency
    }
    for user in existing_user:
        user_ref = users_ref.document(user.id)
        user_data = serialize_firestore_document(user_ref.get())
        information = json.dumps(user_data)
        information2 = json.loads(information)
        context['user_info'] = information2
        context['user_info_dict'] = information
    return render(request, 'admin_tools.html', context)
