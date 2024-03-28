import ast
import random
from datetime import datetime
from random import randint

import concurrent.futures
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model, update_session_auth_hash
import os
import json
import firebase_admin
from django.views.decorators.csrf import csrf_exempt
from firebase_admin import credentials, firestore
from django.conf import settings
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.mail import send_mail

from shop.forms import UserRegisterForm, User

json_file_path = os.path.join(settings.BASE_DIR, "shop", "static", "key2.json")
cred = credentials.Certificate(json_file_path)
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)
db = firestore.client()

country_dict = {
    "231": "Afghanistan",
    "244": "Åland Islands",
    "230": "Albania",
    "38": "Algeria",
    "39": "American Samoa",
    "40": "Andorra",
    "41": "Angola",
    "42": "Anguilla",
    "232": "Antarctica",
    "43": "Antigua and Barbuda",
    "44": "Argentina",
    "45": "Armenia",
    "46": "Aruba",
    "24": "Australia",
    "2": "Austria",
    "47": "Azerbaijan",
    "48": "Bahamas",
    "49": "Bahrain",
    "50": "Bangladesh",
    "51": "Barbados",
    "52": "Belarus",
    "3": "Belgium",
    "53": "Belize",
    "54": "Benin",
    "55": "Bermuda",
    "56": "Bhutan",
    "34": "Bolivia",
    "233": "Bosnia and Herzegovina",
    "57": "Botswana",
    "234": "Bouvet Island",
    "58": "Brazil",
    "235": "British Indian Ocean Territory",
    "59": "Brunei",
    "236": "Bulgaria",
    "60": "Burkina Faso",
    "61": "Burma (Myanmar)",
    "62": "Burundi",
    "63": "Cambodia",
    "64": "Cameroon",
    "4": "Canada",
    "65": "Cape Verde",
    "237": "Cayman Islands",
    "66": "Central African Republic",
    "67": "Chad",
    "68": "Chile",
    "5": "China",
    "238": "Christmas Island",
    "239": "Cocos (Keeling) Islands",
    "69": "Colombia",
    "70": "Comoros",
    "71": "Congo, Dem. Republic",
    "72": "Congo, Republic",
    "240": "Cook Islands",
    "73": "Costa Rica",
    "74": "Croatia",
    "75": "Cuba",
    "76": "Cyprus",
    "16": "Czech Republic",
    "20": "Denmark",
    "77": "Djibouti",
    "78": "Dominica",
    "79": "Dominican Republic",
    "80": "East Timor",
    "81": "Ecuador",
    "82": "Egypt",
    "83": "El Salvador",
    "84": "Equatorial Guinea",
    "85": "Eritrea",
    "86": "Estonia",
    "87": "Ethiopia",
    "88": "Falkland Islands",
    "89": "Faroe Islands",
    "90": "Fiji",
    "7": "Finland",
    "8": "France",
    "241": "French Guiana",
    "242": "French Polynesia",
    "243": "French Southern Territories",
    "91": "Gabon",
    "92": "Gambia",
    "93": "Georgia",
    "1": "Germany",
    "94": "Ghana",
    "97": "Gibraltar",
    "9": "Greece",
    "96": "Greenland",
    "95": "Grenada",
    "98": "Guadeloupe",
    "99": "Guam",
    "100": "Guatemala",
    "101": "Guernsey",
    "102": "Guinea",
    "103": "Guinea-Bissau",
    "104": "Guyana",
    "105": "Haiti",
    "106": "Heard Island and McDonald Islands",
    "108": "Honduras",
    "22": "HongKong",
    "143": "Hungary",
    "109": "Iceland",
    "110": "India",
    "111": "Indonesia",
    "112": "Iran",
    "113": "Iraq",
    "26": "Ireland",
    "29": "Israel",
    "10": "Italy",
    "32": "Ivory Coast",
    "115": "Jamaica",
    "11": "Japan",
    "116": "Jersey",
    "117": "Jordan",
    "118": "Kazakhstan",
    "119": "Kenya",
    "120": "Kiribati",
    "121": "Dem. Republic of Korea",
    "122": "Kuwait",
    "123": "Kyrgyzstan",
    "124": "Laos",
    "125": "Latvia",
    "126": "Lebanon",
    "127": "Lesotho",
    "128": "Liberia",
    "129": "Libya",
    "130": "Liechtenstein",
    "131": "Lithuania",
    "12": "Luxemburg",
    "132": "Macau",
    "133": "Macedonia",
    "134": "Madagascar",
    "135": "Malawi",
    "136": "Malaysia",
    "137": "Maldives",
    "138": "Mali",
    "139": "Malta",
    "114": "Man Island",
    "140": "Marshall Islands",
    "141": "Martinique",
    "142": "Mauritania",
    "35": "Mauritius",
    "144": "Mayotte",
    "145": "Mexico",
    "146": "Micronesia",
    "147": "Moldova",
    "148": "Monaco",
    "149": "Mongolia",
    "150": "Montenegro",
    "151": "Montserrat",
    "152": "Morocco",
    "153": "Mozambique",
    "154": "Namibia",
    "155": "Nauru",
    "156": "Nepal",
    "13": "Netherlands",
    "157": "Netherlands Antilles",
    "158": "New Caledonia",
    "27": "New Zealand",
    "159": "Nicaragua",
    "160": "Niger",
    "31": "Nigeria",
    "161": "Niue",
    "162": "Norfolk Island",
    "245": "Northern Ireland",
    "163": "Northern Mariana Islands",
    "23": "Norway",
    "164": "Oman",
    "165": "Pakistan",
    "166": "Palau",
    "167": "Palestinian Territories",
    "168": "Panama",
    "169": "Papua New Guinea",
    "170": "Paraguay",
    "171": "Peru",
    "172": "Philippines",
    "173": "Pitcairn",
    "14": "Poland",
    "15": "Portugal",
    "174": "Puerto Rico",
    "175": "Qatar",
    "176": "Reunion Island",
    "36": "Romania",
    "177": "Russian Federation",
    "178": "Rwanda",
    "179": "Saint Barthelemy",
    "180": "Saint Kitts and Nevis",
    "181": "Saint Lucia",
    "182": "Saint Martin",
    "183": "Saint Pierre and Miquelon",
    "184": "Saint Vincent and the Grenadines",
    "185": "Samoa",
    "186": "San Marino",
    "187": "São Tomé and Príncipe",
    "188": "Saudi Arabia",
    "189": "Senegal",
    "190": "Serbia",
    "191": "Seychelles",
    "192": "Sierra Leone",
    "25": "Singapore",
    "37": "Slovakia",
    "193": "Slovenia",
    "194": "Solomon Islands",
    "195": "Somalia",
    "30": "South Africa",
    "196": "South Georgia and the South Sandwich Islands",
    "28": "South Korea",
    "6": "Spain",
    "197": "Sri Lanka",
    "198": "Sudan",
    "199": "Suriname",
    "200": "Svalbard and Jan Mayen",
    "201": "Swaziland",
    "18": "Sweden",
    "19": "Switzerland",
    "202": "Syria",
    "203": "Taiwan",
    "204": "Tajikistan",
    "205": "Tanzania",
    "206": "Thailand",
    "33": "Togo",
    "207": "Tokelau",
    "208": "Tonga",
    "209": "Trinidad and Tobago",
    "210": "Tunisia",
    "211": "Turkey",
    "212": "Turkmenistan",
    "213": "Turks and Caicos Islands",
    "214": "Tuvalu",
    "215": "Uganda",
    "216": "Ukraine",
    "217": "United Arab Emirates",
    "17": "United Kingdom",
    "21": "United States",
    "218": "Uruguay",
    "219": "Uzbekistan",
    "220": "Vanuatu",
    "107": "Vatican City State",
    "221": "Venezuela",
    "222": "Vietnam",
    "223": "Virgin Islands (British)",
    "224": "Virgin Islands (U.S.)",
    "225": "Wallis and Futuna",
    "226": "Western Sahara",
    "227": "Yemen",
    "228": "Zambia",
    "229": "Zimbabwe"
}


def home_page(request):
    return render(request, 'home.html')


@login_required
def form_page(request):
    documents = []
    search_term = ''
    if request.method == 'POST':
        search_term = request.POST.get('number').upper()

        db = firestore.client()
        query = db.collection('item').where('name', '==', search_term)
        documents = query.stream()

    cart = get_cart(request)
    quantity = 1
    inside = False
    for prod in cart:
        if search_term == prod['name']:
            inside = True
            quantity = prod['quantity']
            break

    context = {
        'documents': [doc.to_dict() for doc in documents],
        'search_term': search_term,
        'inside': inside,
        'quantity': quantity,
        'is_authenticated': 'False',
        'in_cart': 'False',
        'cart': cart
    }

    return render(request, 'shop_page.html', context)


@login_required
def cart_page(request):
    context = {
        'documents': sorted(get_cart(request), key=lambda x: x['number'])
    }
    return render(request, 'cart.html', context=context)


def fetch_numbers(request):
    search_term = request.GET.get('term', '').lower()
    numbers = []

    if search_term != '':
        # Using Firestore query to filter documents
        name_query = db.collection('item').where('name', '>=', search_term).where('name', '<=',
                                                                                  search_term + '\uf8ff').stream()

        # Filter the results in Python for the 'quantity' field
        numbers = [doc.to_dict().get('name', '') for doc in name_query if
                   search_term in doc.to_dict().get('name', '').lower() and
                   doc.to_dict().get('quantity', 0) > 0]

    return JsonResponse(numbers, safe=False)


# Create your views here.
def add_to_cart(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        product = ast.literal_eval(data.get('document'))

        email = request.user.email  # Replace with actual user email
        print(email)
        quantity = 1  # Replace with actual quantity
        price = product['price']  # Replace with actual price
        name = product['name']  # Replace with actual product name
        image = product['image-url']
        maximum_quantity = product['quantity']
        description = product['description']

        cart_ref = db.collection("Cart")

        cart_items = cart_ref.where('emailOwner', '==', email).get()
        cart_size = len(cart_items)
        item_number = cart_size + 1

        new_cart_item = {
            'description': description,
            'stone': product['stone'],
            'material': product['material'],
            'plating': product['plating'],
            "emailOwner": email,
            'image_url': image,
            "name": name,
            "price": price,
            "quantity": quantity,
            "number": item_number,
            'quantity_max': maximum_quantity
        }
        cart_ref.add(new_cart_item)

        return JsonResponse({'status': 'success', 'quantity': quantity, 'number': item_number, 'sum': price})
    return JsonResponse({'status': 'error'}, status=400)


def update_quantity(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        product_id = data.get('product_id')
        quantity_change = data.get('quantity_change')  # Will be 1 or -1
        document = ast.literal_eval(data.get('document'))
        quantity_max = 0
        try:
            quantity_max = document['quantity_max']
        except:
            quantity_max = document['quantity']

        cart_ref = db.collection('Cart')

        # Get current quantity and update
        email = request.user.email
        docs = cart_ref.where('emailOwner', '==', email).where('name', '==', product_id).limit(1).stream()
        for doc in docs:
            current_quantity = doc.to_dict().get('quantity', 0)
            new_quantity = max(current_quantity + quantity_change, 1)  # Ensure quantity doesn't go below 0
            if new_quantity <= quantity_max:

                doc.reference.update({'quantity': new_quantity})

                return JsonResponse({'status': 'success', 'quantity': new_quantity,
                                     'sum': "€" + str(round(new_quantity * document['price'], 1))})
            else:
                return JsonResponse({'status': 'error', 'message': 'You have reached maximum quantity'}, status=400)
        else:
            return JsonResponse({'status': 'error', 'message': 'Product not found'}, status=404)

    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)


def update_quantity_slider(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        product_id = data.get('product_id')
        quantity_new = data.get('quantity_new')
        document = data.get('document')

        cart_ref = db.collection('Cart')

        # Get current quantity and update
        email = request.user.email
        docs = cart_ref.where('emailOwner', '==', email).where('name', '==', product_id).limit(1).stream()
        for doc in docs:
            # Update the quantity in Firestore
            doc.reference.update({'quantity': int(quantity_new)})
            sum_value = round(float(quantity_new) * float(document['price']), 2)
            return JsonResponse(
                {'status': 'success', 'quantity': quantity_new, 'product_id': product_id, 'sum': "€" + str(sum_value)})
        else:
            return JsonResponse({'status': 'error', 'message': 'Product not found'}, status=404)

    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)


def update_quantity_input(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            product_id = data.get('product_id')
            quantity_new = data.get('quantity_new')
            price = float(data.get('price'))
            cart_ref = db.collection('Cart')
            email = request.user.email  # Replace with actual user email

            cart_items = cart_ref.where('emailOwner', '==', email)

            existing_item = cart_ref.where('emailOwner', '==', email).where('name', '==', product_id).limit(1).get()

            if existing_item:
                doc_ref = existing_item[0].reference
                doc_ref.update({'quantity': quantity_new})
                return JsonResponse({'status': 'success', 'quantity': quantity_new, 'product_id': product_id,
                                     'sum': "€" + str(round((quantity_new * price), 2)), 'was_inside': 'True'})

            else:
                product = json.loads(data.get('document'))

                number_in_cart = len(cart_items.get()) + 1

                new_cart_item = {
                    'description': product['description'],
                    'stone': product['stone'],
                    'material': product['material'],
                    'plating': product['plating'],
                    "emailOwner": email,
                    'image_url': product['image-url'],
                    "name": product['name'],
                    "price": price,
                    "quantity": quantity_new,
                    "number": number_in_cart,
                    'quantity_max': product['quantity']
                }
                cart_ref.add(new_cart_item)
                return JsonResponse({'status': 'success', 'quantity': quantity_new, 'product_id': product_id,
                                     'sum': "€" + str(round((quantity_new * price), 2)), 'was_inside': 'False',
                                     'number': number_in_cart})
        except Exception as e:
            print(f"Error updating cart: {e}")
            return JsonResponse({'status': 'error', 'message': 'An error occurred while processing your request'},
                                status=500)


    else:
        return JsonResponse({'status': 'error', 'message': 'Product not found'}, status=404)

    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)


def get_cart(request):
    # Access the Firebase database

    cart_ref = db.collection('Cart')
    email = request.user.email
    # Get all the documents
    docs = cart_ref.where('emailOwner', '==', email).stream()

    cart = []
    for doc in docs:
        description = doc.to_dict().get('description', '')
        if description:
            safe_description = description.encode('utf-8').decode('utf-8')
        else:
            safe_description = ''
        cart.append({'name': doc.to_dict().get('name'), 'quantity': doc.to_dict().get('quantity'),
                     'number': doc.to_dict().get('number'), 'image_url': doc.to_dict().get('image_url'),
                     'description': safe_description, 'quantity_max': doc.to_dict().get('quantity_max'),
                     'price': doc.to_dict().get('price'),
                     'stone': doc.to_dict().get('stone'),
                     'plating': doc.to_dict().get('plating'),
                     'material': doc.to_dict().get('material'),
                     'sum': str(round(doc.to_dict().get('price') * doc.to_dict().get('quantity'), 1))})
    return cart


def deleteProduct(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        name = data.get('document_id')
        cart_ref = db.collection('Cart')
        email = request.user.email
        docs = cart_ref.where('emailOwner', '==', email).where('name', '==', name).stream()
        for doc in docs:
            doc.reference.delete()

        remaining_docs = cart_ref.where('emailOwner', '==', email).order_by('number').stream()
        new_number = 1
        updated_documents = []
        for doc in remaining_docs:
            doc.reference.update({'number': new_number})
            updated_documents.append({'id': doc.to_dict().get('name', ''), 'number': new_number})
            new_number += 1

        return JsonResponse({'status': 'success', 'updated_documents': updated_documents})
    return JsonResponse({'status': 'error'}, status=400)


def sort_documents(request):
    order_by = request.GET.get('order_by', 'name')
    direction = request.GET.get('direction', 'asc')

    # Get documents from Firebase
    documents = get_cart(request)

    if order_by == 'sum':
        key_function = lambda x: x.get('price', 0) * x.get('quantity', 0)
    else:
        key_function = lambda x: x.get(order_by, "")

    sorted_documents = sorted(documents, key=key_function, reverse=(direction == 'desc'))

    return JsonResponse({'documents': sorted_documents})

def get_new_user_id():
    @firestore.transactional
    def increment_user_id(transaction, user_counter_ref):
        snapshot = user_counter_ref.get(transaction=transaction)
        last_user_id = snapshot.get('lastUserId') if snapshot.exists else 3000
        new_user_id = last_user_id + 1
        transaction.update(user_counter_ref, {'lastUserId': new_user_id})
        return new_user_id

    metadata_collection = db.collection('metadata')
    user_counter_ref = metadata_collection.document('userCounter')
    transaction = db.transaction()
    new_user_id = increment_user_id(transaction, user_counter_ref)
    return new_user_id

def register(request):
    form = UserRegisterForm()
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():

            users_ref = db.collection('users')
            email = form.cleaned_data.get('email')

            existing_user = users_ref.where('email', '==', email).limit(1).get()

            if list(existing_user):  # Convert to list to check if it's non-empty
                print('Error: User with this Email already exists.')
                form.add_error('email', 'User with this Email already exists.')
                return render(request, 'registration/register.html', {'form': form})
            else:

                user_id = get_new_user_id()
                current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                new_user = {
                    'Enabled': 'True',
                    "display_name": "undefined",
                    'social_title': "",
                    'first_name': "",
                    'last_name': "",
                    'email': email,
                    'birthday': "",
                    'country': "undefined",
                    "agent_number": "undefined",
                    'price_category': 'Default',
                    'receive_offers': False,
                    'receive_newsletter': False,
                    'registrationDate': current_time,
                    'userId': user_id,

                }
                users_ref.add(new_user)

                username = form.cleaned_data.get('username')
                password = form.cleaned_data.get('password1')
                form.save()
                user = authenticate(username=username, password=password)
                if user:
                    login(request, user)
                    return redirect('home')
    else:
        form = UserRegisterForm()
    return render(request, 'registration/register.html', {'form': form, 'errors': form.errors})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                email = form.cleaned_data.get('email') or user.email

                # Query Firebase Firestore to check the user's Enabled status
                users_ref = db.collection('users')
                firebase_user_doc = users_ref.where('email', '==', email).limit(1).get()
                if firebase_user_doc and firebase_user_doc[0].to_dict().get('Enabled', True) == False:
                    # Redirect to home with an error message
                    messages.error(request, "Your account was disabled")
                    form.add_error(None, "Your account was disabled")
                    return render(request, 'registration/login.html', {'form': form})
                else:
                    # Proceed to log the user in
                    login(request, user)
                    return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('home')


def fetch_order_detail(order_doc_path):
    path_parts = order_doc_path.split('/')
    if len(path_parts) == 2:
        collection_name, document_id = path_parts
        order_doc_ref = db.collection(collection_name).document(document_id)
        order_doc = order_doc_ref.get()
        if order_doc.exists:
            return order_doc.to_dict()
    return None


def update_email_in_db(old_email, new_email):
    # Define a mapping of collections to their respective email fields
    collection_email_fields = {
        'Cart': 'emailOwner',
        'Favourites': 'email',
        'Order': 'emailOwner',
        'Orders': 'email',
        'Addresses': 'email',
    }

    # Loop through the mapping
    for collection_name, email_field in collection_email_fields.items():
        try:
            # Reference the collection
            collection_ref = db.collection(collection_name)
            # Query for documents with the old email
            docs_to_update = collection_ref.where(email_field, '==', old_email).get()
            # Update each document with the new email
            for doc in docs_to_update:
                doc.reference.update({email_field: new_email})
        except Exception as e:
            # Log the error e, for example using logging library or print statement
            print(f"Error updating {collection_name}: {str(e)}")
            # Optionally, handle the error based on your application's requirements

    return "Updated"


@csrf_exempt
@login_required
def update_user_account(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            old_data = data.get('old')
            new_data = data.get('new')

            old_email = old_data['email']
            new_email = new_data['email']

            users_ref = db.collection('users')

            # Check for existing user by email
            existing_users = users_ref.where('email', '==', old_email).limit(1).get()

            if new_data['email'] != old_email:
                existing_user_with_new_email = users_ref.where('email', '==', new_email).limit(1).get()
                if len(existing_user_with_new_email) > 0:
                    return JsonResponse({'status': 'error', 'message': 'User with this email exists.'}, status=400)
                User = get_user_model()
                try:
                    user_instance = User.objects.get(email=old_email)
                    user_instance.email = new_email  # Update the email

                except User.DoesNotExist:
                    return JsonResponse({'status': 'error', 'message': 'User not found.'}, status=404)

                try:
                    update_email_in_db(old_email, new_email)
                    # Optionally use update_email_in_db_result for further logic
                except Exception as e:
                    # Log the exception e
                    return JsonResponse(
                        {'status': 'error', 'message': 'An error occurred while updating documents in Firestore.'},
                        status=500)


            else:
                User = get_user_model()
                try:
                    # Retrieve the user instance
                    user_instance = User.objects.get(email=old_email)
                except User.DoesNotExist:
                    return JsonResponse({'status': 'error', 'message': 'User not found.'}, status=404)

            social_title = old_data['social_title'] if 'id_gender' not in new_data else "Mr" if new_data[
                                                                                                    'id_gender'] == "1" else "Mrs"
            receive_newsletter = old_data['receive_newsletter'] if 'newsletter' not in new_data else True if new_data[
                                                                                                                 'newsletter'] == "1" else False
            receive_offers = old_data['receive_offers'] if 'optin' not in new_data else True if new_data[
                                                                                                    'optin'] == "1" else False
            password = new_data['password']

            # Check if the provided password matches the user's password
            if not user_instance.check_password(password):
                return JsonResponse({'status': 'error', 'message': 'Incorrect password.'}, status=400)

            new_password = new_data.get('new_password', '')
            if new_password:  # This checks if the new_password string is not empty
                user_instance.set_password(new_password)
                user_instance.save()  # Don't forget to save the user object after setting the new password
                update_session_auth_hash(request, user_instance)

            user_instance.save()

            for user in existing_users:
                user_ref = users_ref.document(user.id)
                user_ref.update({
                    'social_title': social_title,
                    'first_name': new_data['firstname'],
                    'last_name': new_data['lastname'],
                    'email': new_data['email'],
                    'birthday': new_data['birthday'],
                    'receive_newsletter': receive_newsletter,
                    'receive_offers': receive_offers,
                })
                return JsonResponse({'status': 'success', 'message': 'User updated successfully.'})

            return JsonResponse({'status': 'success', 'message': 'User account updated successfully.'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=400)


@login_required
def delete_address(request, address_id):
    addresses_ref = db.collection('Addresses')
    # Query the address by its unique ID
    address_to_delete = addresses_ref.where('address_id', '==', address_id).limit(1).get()

    # Proceed if the request method is POST
    if request.method == 'POST':
        try:
            if address_to_delete:
                # Firestore delete operation
                for address in address_to_delete:
                    address_ref = addresses_ref.document(address.id)
                    address_ref.delete()  # Delete the document
                # Return a success message
                return JsonResponse({'status': 'success', 'message': 'Address deleted successfully.'})
            else:
                # If the address does not exist
                return JsonResponse({'status': 'error', 'message': 'Address not found.'}, status=404)
        except Exception as e:
            # Return an error message if an exception occurs
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

        # If the request method is not POST, inform the user that the method is not allowed
    context = {
        'feature_name': 'new_address',
    }
    return render(request, 'profile/profile_addresses.html', context=context)


def generate_unique_address_id():
    while True:
        # Generate a random 8-digit number
        address_id = random.randint(10000000, 99999999)

        # Check if this ID is already in use
        addresses_db = firestore.client().collection('Addresses')
        existing_address = addresses_db.where('address_id', '==', address_id).get()

        # If the ID is not in use, it's unique, and we can return it
        if not existing_address:
            return address_id


@csrf_exempt
@login_required
def create_address(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            new_data = data.get('address_data')
            if not new_data:  # Check if new_data is None or empty
                return JsonResponse({'status': 'error', 'message': 'Invalid data.'}, status=400)
            unique_address_id = generate_unique_address_id()
            addresses_db = db.collection('Addresses')

            address_document = {
                'address_name': new_data['alias'],
                'first_name': new_data['firstname'],
                'last_name': new_data['lastname'],
                'company': new_data['company'],
                'real_address': new_data['address1'],
                'address_complement': new_data['address2'],
                'postal_code': new_data['postcode'],
                'city': new_data['city'],
                'country': country_dict[new_data['id_country']],
                'phone': new_data['phone'],
                'email': request.user.email,
                'address_id': f"{unique_address_id}"
            }
            addresses_db.add(address_document)
            return JsonResponse({'status': 'success', 'message': 'Address updated successfully.'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    email = request.user.email
    users_ref = db.collection('users')
    information = []
    # Check for existing user by email
    existing_users = users_ref.where('email', '==', email).limit(1).get()

    if existing_users:
        for user in existing_users:
            ref = users_ref.document(user.id)
    context = {
        'feature_name': 'new_address',
        'user_ref': ref.get().to_dict()
    }
    return render(request, 'profile.html', context=context)


@login_required
def update_address(request, address_id):
    addresses_ref = db.collection('Addresses')
    existing_address = addresses_ref.where('address_id', '==', address_id).limit(1).get()
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            old_data = data.get('old')
            new_data = data.get('new')
            if existing_address:
                for address in existing_address:
                    address_ref = addresses_ref.document(address.id)
                    address_ref.update({
                        'address_name': new_data['alias'],
                        'first_name': new_data['firstname'],
                        'last_name': new_data['lastname'],
                        'company': new_data['company'],
                        'real_address': new_data['address1'],
                        'address_complement': new_data['address2'],
                        'postal_code': new_data['postcode'],
                        'city': new_data['city'],
                        'country': country_dict[new_data['id_country']],
                        'phone': new_data['phone'],
                    })
                return JsonResponse({'status': 'success', 'message': 'Address updated successfully.'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    if existing_address:
        address_dict = {}
        for address in existing_address:
            address_ref = addresses_ref.document(address.id)
            address_dict = address_ref.get().to_dict()
        context = {
            'feature_name': 'update_address',
            'address': address_dict,
            'address_dict': json.dumps(address_dict),
        }
        # print(address_dict)
        return render(request, 'profile.html', context=context)
    return JsonResponse({'status': 'error'}, status=400)

def change_favorite_state(request):
    if request.method == 'POST':

        data = json.loads(request.body)
        item = json.loads(data.get('item'))
        isFav = data.get('alreadyFavourite') == "true"
        # Initialize Firestore DB
        db = firestore.client()

        # Reference to the 'Favourites' collection
        cart_ref = db.collection('Favourites')

        # User's email from the request
        email = request.user.email

        if isFav:
            # Query for documents where email and name_id match to delete
            fav_docs = cart_ref.where('email', '==', email).where('name', '==', item['name']).stream()

            # Iterate through the query results and delete each document
            for doc in fav_docs:
                doc.reference.delete()
            return JsonResponse({"isFavourite": "false", "item": json.dumps(item)})
        else:
            # Add a new favorite item to the database
            new_fav = item.copy()  # Assuming 'item' is a dictionary containing the necessary fields
            new_fav['email'] = email  # Add the user's email to the item
            cart_ref.add(new_fav)

            return JsonResponse({"isFavourite": "true", "item": json.dumps(item)})
    return JsonResponse({"status": "error", 'message': 'Nonexistent method'})

def serialize_firestore_document(doc):
    # Convert a Firestore document to a dictionary, handling DatetimeWithNanoseconds
    doc_dict = doc.to_dict()
    for key, value in doc_dict.items():
        if isinstance(value, datetime):
            # Convert datetime to string (ISO format)
            doc_dict[key] = value.isoformat()
    return doc_dict


@login_required
def profile(request, feature_name):
    orders_ref = db.collection("Orders")
    email = request.user.email
    orders = []
    docs_orders = orders_ref.where('email', '==', email).stream()
    order_details = {}

    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_order = {}
        for doc in docs_orders:
            order_info = doc.to_dict()
            order_id = order_info.get('order_id')
            if not order_id:
                order_id = order_info.get('order-id')

            # Assuming `order_info.get('date')` returns a datetime object
            firebase_date = order_info.get('date')

            # Format the datetime object to the desired format (YYYY-MM-DD)
            formatted_date = firebase_date.strftime("%Y-%m-%d") if firebase_date else None

            orders.append({
                'Status': order_info.get('Status'),
                'date': formatted_date,  # Use the formatted date
                'email': email,  # Assuming `email` is defined elsewhere in your code
                'list': order_info.get('list'),
                'order_id': order_id,
                'sum': order_info.get('price')
            })
            order_details[order_id] = []

            # Schedule the fetch operation for each document in the order list
            for order_doc_ref in order_info.get('list', []):

                if type(order_doc_ref) is str:
                    order_doc_path = order_doc_ref  # Extracting the document path
                else:
                    order_doc_path = order_doc_ref.path
                future = executor.submit(fetch_order_detail, order_doc_path)
                future_to_order[future] = order_id

        # Process as completed
        for future in concurrent.futures.as_completed(future_to_order):
            order_id = future_to_order[future]
            order_doc_data = future.result()
            if order_doc_data:
                order_details[order_id].append(order_doc_data)

    context = {
        'orders': orders,
        'products': order_details,
        'feature_name': feature_name,
    }
    if feature_name == "account":
        users_ref = db.collection('users')
        # Check for existing user by email
        existing_users = users_ref.where('email', '==', email).limit(1).get()
        if existing_users:
            for user in existing_users:
                user_ref = users_ref.document(user.id)
                user_data = serialize_firestore_document(user_ref.get())
                information = json.dumps(user_data)  # Now it should work without errors
                information2 = json.loads(information)
                context['user_info'] = information2
                context['user_info_dict'] = information

    if feature_name == "addresses":
        addresses_ref = db.collection('Addresses')
        addresses = []
        existing_addresses = addresses_ref.where('email', '==', email).get()
        if existing_addresses:
            for address in existing_addresses:
                address_red = addresses_ref.document(address.id)
                information = json.dumps(address_red.get().to_dict())
                information2 = json.loads(information)
                addresses.append(information2)
                context['my_addresses'] = addresses
                context['addresses_dict'] = information

    return render(request, 'profile.html', context=context)


def send_email(request):
    if request.method == 'POST':
        # Создаю order

        cart = get_cart(request)
        order_ref = db.collection("Order")
        orders_ref = db.collection("Orders")

        email = request.user.email
        order_id = randint(1000000, 100000000)
        item_refs = []
        names = []
        sum = 0
        for order_item in cart:
            description = order_item.get('description')
            price = order_item.get('price')
            quantity = order_item.get('quantity')
            name = order_item.get('name')
            names.append(name)
            image_url = order_item.get('image_url')
            sum += round(price * quantity, 1)
            new_order_item = {
                'description': description,
                "emailOwner": email,
                'image_url': image_url,
                "name": name,
                "order_id": order_id,
                "price": price,
                "quantity": quantity,
            }
            doc_ref = order_ref.document()
            doc_ref.set(new_order_item)
            item_refs.append(doc_ref)
        new_order = {
            'Status': 'Awaiting',
            'date': datetime.now(),  # Current date and time
            'email': email,
            'list': [ref.path for ref in item_refs],  # Using document paths as references
            'order_id': order_id,
            'order-id': order_id,
            'price': round(sum, 1)
        }
        orders_ref.add(new_order)

        for delete_name in names:
            clear_cart(email, delete_name)

        # Define email parameters
        subject = 'Test mail'
        message = 'Test mail from order-form!'
        recipient_list = [str(request.user.email), 'westadatabase@gmail.com']  # replace with your recipient list
        print(recipient_list)
        # Send the email
        send_mail(subject, message, 'setting.EMAIL_HOST_USER', recipient_list)
        return JsonResponse({'status': 'success', 'redirect_name': 'home'})
    return JsonResponse({'status': 'error'}, status=400)


def clear_cart(email, name):
    cart_ref = db.collection('Cart')

    docs = cart_ref.where('emailOwner', '==', email).where('name', '==', name).stream()
    for doc in docs:
        doc.reference.delete()


@login_required
def catalog_view(request):
    return render(request, 'catalog.html')


def get_actual_product(catalog_product_name):
    item_ref = db.collection("item")

    docs = (item_ref
            .where('name', '==', catalog_product_name).stream())
    for doc in docs:
        return doc.to_dict()


def add_to_cart_from_catalog(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        product_name = data.get('document')
        new_quantity = data.get('quantity')
        document = get_actual_product(product_name)
        try:
            cart_ref = db.collection('Cart')
            email = request.user.email  # Replace with actual user email

            cart_items = cart_ref.where('emailOwner', '==', email)

            existing_item = cart_ref.where('emailOwner', '==', email).where('name', '==', product_name).limit(1).get()
            cart_size = len(get_cart(request))

            subtotal = 0

            if existing_item:
                doc_ref = existing_item[0].reference
                doc_ref.update({'quantity': new_quantity})
                new_sum = round((new_quantity * document['price']), 2)
                for c in get_cart(request):
                    subtotal += float(c['sum'])
                subtotal = round((subtotal), 2)
                return JsonResponse({'status': 'success', 'quantity': new_quantity, 'product_id': product_name,
                                     'sum': "€" + str(new_sum), 'was_inside': 'True', 'product': document,
                                     'cart_size': cart_size, 'subtotal': subtotal})

            else:
                number_in_cart = len(cart_items.get()) + 1

                new_cart_item = {
                    'description': document['description'],
                    'stone': document['stone'],
                    'material': document['material'],
                    'plating': document['plating'],
                    "emailOwner": email,
                    'image_url': document['image-url'],
                    "name": document['name'],
                    "price": document['price'],
                    "quantity": new_quantity,
                    "number": number_in_cart,
                    'quantity_max': document['quantity']
                }
                cart_ref.add(new_cart_item)
                new_sum = round((new_quantity * document['price']), 2)
                for c in get_cart(request):
                    subtotal += float(c['sum'])
                subtotal = round((subtotal), 2)
                return JsonResponse({'status': 'success', 'quantity': new_quantity, 'product_id': product_name,
                                     'sum': "€" + str(round((new_quantity * document['price']), 2)),
                                     'was_inside': 'False',
                                     'number': number_in_cart, 'product': document, 'cart_size': cart_size + 1,
                                     'subtotal': subtotal})
        except Exception as e:
            print(f"Error updating cart: {e}")
            return JsonResponse({'status': 'error', 'message': 'An error occurred while processing your request'},
                                status=500)


def getCartToBase(request):
    return JsonResponse({'cart': get_cart(request)})


def is_admin(user):
    return user.is_authenticated and user.is_staff


@login_required
@user_passes_test(is_admin)
def admin_tools(request, feature_name):
    context = {

        "feature_name": feature_name,
    }
    return render(request, 'admin_tools.html', context)
@login_required
@user_passes_test(is_admin)  # Adjust the test as needed
def enable_users(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_ids = data.get('userIds')
            if user_ids is None:
                raise ValueError("User IDs not provided")

            # Call the helper function to enable users
            update_user_enabled_status(user_ids, True)

            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

@login_required
@user_passes_test(is_admin)
def disable_users(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_ids = data.get('userIds')
            if user_ids is None:
                raise ValueError("User IDs not provided")

            # Call the helper function to disable users
            update_user_enabled_status(user_ids, False)

            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)
def update_user_enabled_status(user_ids, enable):
    """
    Updates the 'Enabled' status of users in Firestore based on provided user IDs.
    """
    db = firestore.client()
    batch_limit = 500
    batch_count = 0
    batch = db.batch()

    for user_id in user_ids:
        users_ref = db.collection('users').where('userId', '==', int(user_id))
        docs = users_ref.get()

        for doc in docs:
            doc_ref = db.collection('users').document(doc.id)
            batch.update(doc_ref, {"Enabled": enable})
            batch_count += 1

            if batch_count >= batch_limit:
                batch.commit()
                batch = db.batch()
                batch_count = 0

    if batch_count > 0:
        batch.commit()

    return True
@login_required
@user_passes_test(is_admin)
def delete_users(request):
    if request.method == 'POST':
        try:
            # Load the user IDs from the request body
            data = json.loads(request.body)
            user_ids = data.get('userIds')

            if not user_ids:
                return JsonResponse({'status': 'error', 'message': 'No user IDs provided'}, status=400)

            db = firestore.client()

            # Firestore has a limit of 500 operations per batch
            batch = db.batch()
            operations_count = 0

            for user_id in user_ids:
                # Query for documents with matching userId field
                query = db.collection('users').where('userId', '==', int(user_id))
                docs = query.get()

                for doc in docs:
                    doc_ref = db.collection('users').document(doc.id)
                    batch.delete(doc_ref)
                    operations_count += 1

                    # Commit the batch if it reaches the Firestore limit
                    if operations_count >= 500:
                        batch.commit()
                        batch = db.batch()  # Start a new batch
                        operations_count = 0

            # Commit any remaining operations in the batch
            if operations_count > 0:
                batch.commit()

            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

@login_required
@user_passes_test(is_admin)
def edit_user(request, user_id):
    print("Edit user " + user_id)

    users_ref = db.collection('users').where('userId', '==', int(user_id))
    existing_user = users_ref.limit(1).stream()
    context = {

    }
    for user in existing_user:
        user_data = user.to_dict()
        information = json.dumps(user_data)  # Now it should work without errors
        information2 = json.loads(information)
        context['user_info'] = information2
        context['user_info_dict'] = information
    print(context)
    return render(request, 'admin_tools/AT_UC_edit_user.html', context)


@login_required
@user_passes_test(is_admin)
def view_user(request, user_id):
    print("View user " + user_id)

    users_ref = db.collection('users').where('userId', '==', int(user_id))
    existing_user = users_ref.limit(1).stream()
    context = {

    }
    for user in existing_user:
        user_data = user.to_dict()
        information = json.dumps(user_data)  # Now it should work without errors
        information2 = json.loads(information)
        context['user_info'] = information2
        context['user_info_dict'] = information

    return render(request, 'admin_tools/AT_UC_edit_user.html', context)

