import ast
import random
from datetime import datetime
from random import randint

import concurrent.futures
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
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
orders_ref = db.collection("Orders")
users_ref = db.collection('users')
itemsRef = db.collection('item')
cart_ref = db.collection("Cart")
addresses_ref = db.collection('Addresses')
metadata_ref = db.collection('metadata')
favourites_ref = db.collection('Favourites')
single_order_ref = db.collection("Order")

currency_dict = {
    "1":"Euro",
    "2":"Dollar"
}

groups_dict = {
    "1":"Default",
    "2":"VK3",
    "3":"GH",
    "4":"Default_USD",
    "5": "GH_USD",
}

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


def get_user_category(email):
    user = users_ref.where('email', '==', email).limit(1).get()
    if user:
        for user_info in user:
            user_dict = user_info.to_dict()
            return user_dict['price_category'], user_dict['currency'] if 'currency' in user_dict else "Euro"
    else:
        return "Default", "Euro"
def get_user_info(email):
    user = users_ref.where('email', '==', email).limit(1).get()
    for user_info in user:
        user_dict = user_info.to_dict()
        return user_dict


def get_cart(email):
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


def getCart(request):

    return JsonResponse({'cart': get_cart(request.user.email)})


def update_quantity_input(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            product_id = data.get('product_id')
            quantity_new = data.get('quantity_new')
            price = float(data.get('price'))
            email = request.user.email  # Replace with actual user email

            cart_items = cart_ref.where('emailOwner', '==', email)

            existing_item = cart_ref.where('emailOwner', '==', email).where('name', '==', product_id).limit(1).get()

            if existing_item:
                doc_ref = existing_item[0].reference
                doc_ref.update({'quantity': quantity_new})
                return JsonResponse({'status': 'success', 'quantity': quantity_new, 'product_id': product_id,
                                     'sum': str(round((quantity_new * price), 2)), 'was_inside': 'True'})

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
                                     'sum': str(round((quantity_new * price), 2)), 'was_inside': 'False',
                                     'number': number_in_cart})
        except Exception as e:
            print(f"Error updating cart: {e}")
            return JsonResponse({'status': 'error', 'message': 'An error occurred while processing your request'},
                                status=500)


    else:
        return JsonResponse({'status': 'error', 'message': 'Product not found'}, status=404)


def deleteProduct(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        name = data.get('document_id')
        if data.get('email'):
            email = data.get('email')
        else:
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


def serialize_firestore_document(doc):
    # Convert a Firestore document to a dictionary, handling DatetimeWithNanoseconds
    doc_dict = doc.to_dict()
    for key, value in doc_dict.items():
        if isinstance(value, datetime):
            # Convert datetime to string (ISO format)
            doc_dict[key] = value.isoformat()
    return doc_dict

# Test on is user an admin
def is_admin(user):
    return user.is_authenticated and user.is_staff


@login_required
@user_passes_test(is_admin)
def admin_tools(request, feature_name):
    email = request.user.email
    category, currency = get_user_category(email)
    currency = '€' if currency == 'Euro' else '$'
    context = {
        "feature_name": feature_name,
        'currency':currency
    }
    return render(request, 'admin_tools.html', context)


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

            emails_to_delete = []

            # Firestore has a limit of 500 operations per batch
            batch = db.batch()
            operations_count = 0

            for user_id in user_ids:
                # Query for documents with matching userId field

                docs = users_ref.where('userId', '==', int(user_id)).get()


                for doc in docs:
                    user_data = doc.to_dict()  # Convert document to dictionary
                    if 'email' in user_data:
                        emails_to_delete.append(user_data['email'])
                    doc_ref = users_ref.document(doc.id)
                    batch.delete(doc_ref)
                    operations_count += 1

                    # Commit the batch if it reaches the Firestore limit
                    if operations_count >= 500:
                        batch.commit()
                        batch = db.batch()  # Start a new batch
                        operations_count = 0

            if emails_to_delete:
                User.objects.filter(email__in=emails_to_delete).delete()

            # Commit any remaining operations in the batch
            if operations_count > 0:
                batch.commit()

            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)


def get_acc_data(email):
    existing_user = users_ref.where('email', '==', email).limit(1).stream()
    if existing_user:
        for user in existing_user:
            user_ref = users_ref.document(user.id)
            user_data = serialize_firestore_document(user_ref.get())
            user_info_dict = json.dumps(user_data)
            user_info_parsed = json.loads(user_info_dict)
            return user_info_dict, user_info_parsed
    return False, False

