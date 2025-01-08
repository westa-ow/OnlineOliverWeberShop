import ast
import random
from datetime import datetime
from random import randint
import geoip2.database

import concurrent.futures

import stripe
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
from rest_framework import viewsets, status
from rest_framework.response import Response

from OnlineShop.settings import GEOIP_PATH, GEOIP_config
from shop.forms import UserRegisterForm, User, BannerForm
from django.utils.translation import gettext as _

from shop.models import Banner, PromoCode
from shop.views_scripts.serializers import PromoCodeSerializer

stripe.api_key = settings.STRIPE_SECRET_KEY

db = settings.FIRESTORE_CLIENT
orders_ref = db.collection("Orders")
stones_ref = db.collection("Stones")
users_ref = db.collection('webUsers')
itemsRef = db.collection('item')
cart_ref = db.collection("Cart")
addresses_ref = db.collection('Addresses')
metadata_ref = db.collection('metadata')
favourites_ref = db.collection('Favourites')
single_order_ref = db.collection("Order")
promocodes_ref = db.collection('Promocodes')
active_promocodes_ref = db.collection('ActivePromocodes')

READER = geoip2.database.Reader(GEOIP_config)

countrys_shipping = {'Afghanistan': 8.4, 'Åland Islands': 8.4, 'Albania': 8.4, 'Algeria': 8.4, 'American Samoa': 8.4,
                     'Andorra': 8.4, 'Angola': 8.4, 'Anguilla': 8.4, 'Antarctica': 8.4, 'Antigua and Barbuda': 8.4,
                     'Argentina': 8.4, 'Armenia': 8.4, 'Aruba': 8.4, 'Australia': 8.4, 'Austria': 8.4,
                     'Azerbaijan': 8.4, 'Bahamas': 8.4, 'Bahrain': 8.4, 'Bangladesh': 8.4, 'Barbados': 8.4,
                     'Belarus': 8.4, 'Belgium': 8.4, 'Belize': 8.4, 'Benin': 8.4, 'Bermuda': 8.4, 'Bhutan': 8.4,
                     'Bolivia': 8.4, 'Bosnia and Herzegovina': 8.4, 'Botswana': 8.4, 'Bouvet Island': 8.4,
                     'Brazil': 8.4, 'British Indian Ocean Territory': 8.4, 'Brunei': 8.4, 'Bulgaria': 8.4,
                     'Burkina Faso': 8.4, 'Burma (Myanmar)': 8.4, 'Burundi': 8.4, 'Cambodia': 8.4, 'Cameroon': 8.4,
                     'Canada': 8.4, 'Cape Verde': 8.4, 'Cayman Islands': 8.4, 'Central African Republic': 8.4,
                     'Chad': 8.4, 'Chile': 8.4, 'China': 8.4, 'Christmas Island': 8.4, 'Cocos (Keeling) Islands': 8.4,
                     'Colombia': 8.4, 'Comoros': 8.4, 'Congo, Dem. Republic': 8.4, 'Congo, Republic': 8.4,
                     'Cook Islands': 8.4, 'Costa Rica': 8.4, 'Croatia': 8.4, 'Cuba': 8.4, 'Cyprus': 8.4,
                     'Czech Republic': 8.4, 'Denmark': 8.4, 'Djibouti': 8.4, 'Dominica': 8.4, 'Dominican Republic': 8.4,
                     'East Timor': 8.4, 'Ecuador': 8.4, 'Egypt': 8.4, 'El Salvador': 8.4, 'Equatorial Guinea': 8.4,
                     'Eritrea': 8.4, 'Estonia': 8.4, 'Ethiopia': 8.4, 'Falkland Islands': 8.4, 'Faroe Islands': 8.4,
                     'Fiji': 8.4, 'Finland': 8.4, 'France': 8.4, 'French Guiana': 8.4, 'French Polynesia': 8.4,
                     'French Southern Territories': 8.4, 'Gabon': 8.4, 'Gambia': 8.4, 'Georgia': 8.4, 'Germany': 8.4,
                     'Ghana': 8.4, 'Gibraltar': 8.4, 'Greece': 8.4, 'Greenland': 8.4, 'Grenada': 8.4, 'Guadeloupe': 8.4,
                     'Guam': 8.4, 'Guatemala': 8.4, 'Guernsey': 8.4, 'Guinea': 8.4, 'Guinea-Bissau': 8.4, 'Guyana': 8.4,
                     'Haiti': 8.4, 'Heard Island and McDonald Islands': 8.4, 'Honduras': 8.4, 'HongKong': 8.4,
                     'Hungary': 8.4, 'Iceland': 8.4, 'India': 8.4, 'Indonesia': 8.4, 'Iran': 8.4, 'Iraq': 8.4,
                     'Ireland': 8.4, 'Israel': 8.4, 'Italy': 8.4, 'Ivory Coast': 8.4, 'Jamaica': 8.4, 'Japan': 8.4,
                     'Jersey': 8.4, 'Jordan': 8.4, 'Kazakhstan': 8.4, 'Kenya': 8.4, 'Kiribati': 8.4,
                     'Dem. Republic of Korea': 8.4, 'Kuwait': 8.4, 'Kyrgyzstan': 8.4, 'Laos': 8.4, 'Latvia': 8.4,
                     'Lebanon': 8.4, 'Lesotho': 8.4, 'Liberia': 8.4, 'Libya': 8.4, 'Liechtenstein': 8.4,
                     'Lithuania': 8.4, 'Luxemburg': 8.4, 'Macau': 8.4, 'Macedonia': 8.4, 'Madagascar': 8.4,
                     'Malawi': 8.4, 'Malaysia': 8.4, 'Maldives': 8.4, 'Mali': 8.4, 'Malta': 8.4, 'Man Island': 8.4,
                     'Marshall Islands': 8.4, 'Martinique': 8.4, 'Mauritania': 8.4, 'Mauritius': 8.4, 'Mayotte': 8.4,
                     'Mexico': 8.4, 'Micronesia': 8.4, 'Moldova': 8.4, 'Monaco': 8.4, 'Mongolia': 8.4,
                     'Montenegro': 8.4, 'Montserrat': 8.4, 'Morocco': 8.4, 'Mozambique': 8.4, 'Namibia': 8.4,
                     'Nauru': 8.4, 'Nepal': 8.4, 'Netherlands': 8.4, 'Netherlands Antilles': 8.4, 'New Caledonia': 8.4,
                     'New Zealand': 8.4, 'Nicaragua': 8.4, 'Niger': 8.4, 'Nigeria': 8.4, 'Niue': 8.4,
                     'Norfolk Island': 8.4, 'Northern Ireland': 8.4, 'Northern Mariana Islands': 8.4, 'Norway': 8.4,
                     'Oman': 8.4, 'Pakistan': 8.4, 'Palau': 8.4, 'Palestinian Territories': 8.4, 'Panama': 8.4,
                     'Papua New Guinea': 8.4, 'Paraguay': 8.4, 'Peru': 8.4, 'Philippines': 8.4, 'Pitcairn': 8.4,
                     'Poland': 8.4, 'Portugal': 8.4, 'Puerto Rico': 8.4, 'Qatar': 8.4, 'Reunion Island': 8.4,
                     'Romania': 8.4, 'Russian Federation': 8.4, 'Rwanda': 8.4, 'Saint Barthelemy': 8.4,
                     'Saint Kitts and Nevis': 8.4, 'Saint Lucia': 8.4, 'Saint Martin': 8.4,
                     'Saint Pierre and Miquelon': 8.4, 'Saint Vincent and the Grenadines': 8.4, 'Samoa': 8.4,
                     'San Marino': 8.4, 'São Tomé and Príncipe': 8.4, 'Saudi Arabia': 8.4, 'Senegal': 8.4,
                     'Serbia': 8.4, 'Seychelles': 8.4, 'Sierra Leone': 8.4, 'Singapore': 8.4, 'Slovakia': 8.4,
                     'Slovenia': 8.4, 'Solomon Islands': 8.4, 'Somalia': 8.4, 'South Africa': 8.4,
                     'South Georgia and the South Sandwich Islands': 8.4, 'South Korea': 8.4, 'Spain': 8.4,
                     'Sri Lanka': 8.4, 'Sudan': 8.4, 'Suriname': 8.4, 'Svalbard and Jan Mayen': 8.4, 'Swaziland': 8.4,
                     'Sweden': 8.4, 'Switzerland': 8.4, 'Syria': 8.4, 'Taiwan': 8.4, 'Tajikistan': 8.4, 'Tanzania': 8.4,
                     'Thailand': 8.4, 'Togo': 8.4, 'Tokelau': 8.4, 'Tonga': 8.4, 'Trinidad and Tobago': 8.4,
                     'Tunisia': 8.4, 'Turkey': 8.4, 'Turkmenistan': 8.4, 'Turks and Caicos Islands': 8.4, 'Tuvalu': 8.4,
                     'Uganda': 8.4, 'Ukraine': 8.4, 'United Arab Emirates': 8.4, 'United Kingdom': 8.4,
                     'United States': 8.4, 'Uruguay': 8.4, 'Uzbekistan': 8.4, 'Vanuatu': 8.4, 'Vatican City State': 8.4,
                     'Venezuela': 8.4, 'Vietnam': 8.4, 'Virgin Islands (British)': 8.4, 'Virgin Islands (U.S.)': 8.4,
                     'Wallis and Futuna': 8.4, 'Western Sahara': 8.4, 'Yemen': 8.4, 'Zambia': 8.4, 'Zimbabwe': 8.4}
countrys_vat = {'Afghanistan': 0, 'Åland Islands': 0, 'Albania': 0, 'Algeria': 0, 'American Samoa': 0, 'Andorra': 0,
                'Angola': 0, 'Anguilla': 0, 'Antarctica': 0, 'Antigua and Barbuda': 0, 'Argentina': 0, 'Armenia': 0,
                'Aruba': 0, 'Australia': 0, 'Austria': 20, 'Azerbaijan': 0, 'Bahamas': 0, 'Bahrain': 0, 'Bangladesh': 0,
                'Barbados': 0, 'Belarus': 0, 'Belgium': 21, 'Belize': 0, 'Benin': 0, 'Bermuda': 0, 'Bhutan': 0,
                'Bolivia': 0, 'Bosnia and Herzegovina': 0, 'Botswana': 0, 'Bouvet Island': 0, 'Brazil': 0,
                'British Indian Ocean Territory': 0, 'Brunei': 0, 'Bulgaria': 20, 'Burkina Faso': 0,
                'Burma (Myanmar)': 0, 'Burundi': 0, 'Cambodia': 0, 'Cameroon': 0, 'Canada': 0, 'Cape Verde': 0,
                'Cayman Islands': 0, 'Central African Republic': 0, 'Chad': 0, 'Chile': 0, 'China': 0,
                'Christmas Island': 0, 'Cocos (Keeling) Islands': 0, 'Colombia': 0, 'Comoros': 0,
                'Congo, Dem. Republic': 0, 'Congo, Republic': 0, 'Cook Islands': 0, 'Costa Rica': 0, 'Croatia': 25,
                'Cuba': 0, 'Cyprus': 19, 'Czech Republic': 21, 'Denmark': 25, 'Djibouti': 0, 'Dominica': 0,
                'Dominican Republic': 0, 'East Timor': 0, 'Ecuador': 0, 'Egypt': 0, 'El Salvador': 0,
                'Equatorial Guinea': 0, 'Eritrea': 0, 'Estonia': 22, 'Ethiopia': 0, 'Falkland Islands': 0,
                'Faroe Islands': 0, 'Fiji': 0, 'Finland': 24, 'France': 20, 'French Guiana': 0, 'French Polynesia': 0,
                'French Southern Territories': 0, 'Gabon': 0, 'Gambia': 0, 'Georgia': 0, 'Germany': 19, 'Ghana': 0,
                'Gibraltar': 0, 'Greece': 24, 'Greenland': 0, 'Grenada': 0, 'Guadeloupe': 0, 'Guam': 0, 'Guatemala': 0,
                'Guernsey': 0, 'Guinea': 0, 'Guinea-Bissau': 0, 'Guyana': 0, 'Haiti': 0,
                'Heard Island and McDonald Islands': 0, 'Honduras': 0, 'HongKong': 0, 'Hungary': 27, 'Iceland': 0,
                'India': 0, 'Indonesia': 0, 'Iran': 0, 'Iraq': 0, 'Ireland': 23, 'Israel': 0, 'Italy': 22,
                'Ivory Coast': 0, 'Jamaica': 0, 'Japan': 0, 'Jersey': 0, 'Jordan': 0, 'Kazakhstan': 0, 'Kenya': 0,
                'Kiribati': 0, 'Dem. Republic of Korea': 0, 'Kuwait': 0, 'Kyrgyzstan': 0, 'Laos': 0, 'Latvia': 21,
                'Lebanon': 0, 'Lesotho': 0, 'Liberia': 0, 'Libya': 0, 'Liechtenstein': 8.1, 'Lithuania': 21,
                'Luxemburg': 0, 'Macau': 0, 'Macedonia': 0, 'Madagascar': 0, 'Malawi': 0, 'Malaysia': 0, 'Maldives': 0,
                'Mali': 0, 'Malta': 18, 'Man Island': 0, 'Marshall Islands': 0, 'Martinique': 0, 'Mauritania': 0,
                'Mauritius': 0, 'Mayotte': 0, 'Mexico': 0, 'Micronesia': 0, 'Moldova': 0, 'Monaco': 20, 'Mongolia': 0,
                'Montenegro': 0, 'Montserrat': 0, 'Morocco': 0, 'Mozambique': 0, 'Namibia': 0, 'Nauru': 0, 'Nepal': 0,
                'Netherlands': 21, 'Netherlands Antilles': 0, 'New Caledonia': 0, 'New Zealand': 0, 'Nicaragua': 0,
                'Niger': 0, 'Nigeria': 0, 'Niue': 0, 'Norfolk Island': 0, 'Northern Ireland': 0,
                'Northern Mariana Islands': 0, 'Norway': 0, 'Oman': 0, 'Pakistan': 0, 'Palau': 0,
                'Palestinian Territories': 0, 'Panama': 0, 'Papua New Guinea': 0, 'Paraguay': 0, 'Peru': 0,
                'Philippines': 0, 'Pitcairn': 0, 'Poland': 23, 'Portugal': 23, 'Puerto Rico': 0, 'Qatar': 0,
                'Reunion Island': 0, 'Romania': 19, 'Russian Federation': 0, 'Rwanda': 0, 'Saint Barthelemy': 0,
                'Saint Kitts and Nevis': 0, 'Saint Lucia': 0, 'Saint Martin': 0, 'Saint Pierre and Miquelon': 0,
                'Saint Vincent and the Grenadines': 0, 'Samoa': 0, 'San Marino': 0, 'São Tomé and Príncipe': 0,
                'Saudi Arabia': 0, 'Senegal': 0, 'Serbia': 0, 'Seychelles': 0, 'Sierra Leone': 0, 'Singapore': 0,
                'Slovakia': 20, 'Slovenia': 22, 'Solomon Islands': 0, 'Somalia': 0, 'South Africa': 0,
                'South Georgia and the South Sandwich Islands': 0, 'South Korea': 0, 'Spain': 21, 'Sri Lanka': 0,
                'Sudan': 0, 'Suriname': 0, 'Svalbard and Jan Mayen': 0, 'Swaziland': 0, 'Sweden': 25,
                'Switzerland': 8.1, 'Syria': 0, 'Taiwan': 0, 'Tajikistan': 0, 'Tanzania': 0, 'Thailand': 0, 'Togo': 0,
                'Tokelau': 0, 'Tonga': 0, 'Trinidad and Tobago': 0, 'Tunisia': 0, 'Turkey': 0, 'Turkmenistan': 0,
                'Turks and Caicos Islands': 0, 'Tuvalu': 0, 'Uganda': 0, 'Ukraine': 0, 'United Arab Emirates': 0,
                'United Kingdom': 20, 'United States': 0, 'Uruguay': 0, 'Uzbekistan': 0, 'Vanuatu': 0,
                'Vatican City State': 0, 'Venezuela': 0, 'Vietnam': 0, 'Virgin Islands (British)': 0,
                'Virgin Islands (U.S.)': 0, 'Wallis and Futuna': 0, 'Western Sahara': 0, 'Yemen': 0, 'Zambia': 0,
                'Zimbabwe': 0}

currency_dict = {
    "1": "Euro",
    "2": "Dollar"
}

groups_dict = {
    "1": "Default",
    "2": "VK3",
    "3": "GH",
    "4": "Default_USD",
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


def get_user_prices(request, email):
    if request.user.is_authenticated:
        return get_user_category(email) or ("Default", "Euro")

    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]  # В случае нескольких прокси, берем первый IP
    else:
        ip = request.META.get('REMOTE_ADDR')
    try:
        response = READER.country(ip)
        country_code = response.country.iso_code
        print(country_code)
        if country_code in ['AT', 'BE', 'BG', 'CY', 'CZ', 'DE', 'DK', 'EE', 'ES', 'FI', 'FR', 'GR', 'HR', 'HU', 'IE',
                            'IT', 'LT', 'LU', 'LV', 'MT', 'NL', 'PL', 'PT', 'RO', 'SE', 'SI', 'SK']:
            return "Default", 'Euro'
        elif country_code in ['RU']:
            return "Default_High", 'Euro'
    except geoip2.errors.AddressNotFoundError:
        pass
    return "Default_USD", 'Dollar'


def get_user_session_type(request):
    if request.user.is_authenticated:
        return request.user.email
    else:
        return request.session.session_key


def get_vocabulary_product_card():
    return {
        "In stock": _("In stock"),
        "Less than 5 pieces left!": _("Less than 5 pieces left!"),
        "Plating Material": _("Plating Material"),
        "Stone color": _("Stone color"),
        "Size": _("Size"),
        "Quantity number has to be less than or equal to quantity number in stock or and be greater than 0": _(
            "Quantity number has to be less than or equal to quantity number in stock or and be greater than 0"),
        "Processing": _("Processing"),
        "An error occured": _("An error occured"),
        "Product successfully added to your shopping cart": _("Product successfully added to your shopping cart"),
        "Crystal color": _("Crystal color"),
        "Base material": _("Base material"),
        "Quantity": _("Quantity"),
        "Number of items in your cart": _("Number of items in your cart:"),
        "Subtotal": _("Subtotal"),
        "Continue shopping": _("Continue shopping"),
        "Proceed to checkout": _("Proceed to checkout"),
        "Add to cart": _("Add to cart"),
        "This item is only available for pre-order!": _("This item is only available for pre-order!"),
        "Maximum items for pre-order is 20, minimum is 1": _("Maximum items for pre-order is 20, minimum is 1"),
        "Product width": _("Product width"),
        "Product height": _("Product height"),
        "Chain length": _("Chain length"),
        "Add to favorites": _("Add to favorites"),
        "Remove from favorites": _("Remove from favorites"),
        "Copy link": _("Copy link"),
        "Copied!": _("Copied!"),
        "Reset ": _("Reset this group"),
        "Similar products": _("Similar products"),

    }


def home_page(request):
    context = {
        'address': request.META.get('REMOTE_ADDR'),
        'banners': Banner.objects.all().order_by('priority')
    }

    test_text = _("Welcome to my site.")
    email = get_user_session_type(request)

    category, currency = get_user_prices(request, email)  # Для пользователей валюта определяется по IP

    currency = '€' if currency == 'Euro' else '$'
    info = get_user_info(email) or {}
    sale = round((0 if "sale" not in info else info['sale']) / 100, 3) or 0
    show_quantities = info['show_quantities'] if 'show_quantities' in info else False
    context['currency'] = currency
    context['category'] = category
    context['sale'] = sale
    context['show_quantities'] = show_quantities
    context['hello'] = test_text
    context['vocabulary_dialog'] = get_vocabulary_product_card()
    print(context['hello'])
    return render(request, 'home.html', context)


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
    return {}


def get_address_info(addressId):
    addresses = addresses_ref.where('address_id', '==', addressId).limit(1).get()
    for address in addresses:
        address_dict = address.to_dict()
        return address_dict
    return {}


def get_vat_info(address):
    return countrys_vat.get(address['country'], 0)


def get_shipping_price(address):
    return countrys_shipping.get(address['country'], 0)


def get_cart(email):
    docs = cart_ref.where('emailOwner', '==', email).stream()

    cart = []
    for doc in docs:
        doc_dict = doc.to_dict()  # Call to_dict once

        if len(doc_dict) <= 7:
            continue
        description = doc_dict.get('description', '')

        # Simplify the handling of description encoding if necessary
        safe_description = description.encode('utf-8').decode('utf-8') if description else ''

        cart_item = {
            'name': doc_dict.get('name'),
            'product_name': doc_dict.get('product_name'),
            'quantity': doc_dict.get('quantity'),
            'category': _(doc_dict.get('category', "")) if _(doc_dict.get('category')) is not None else doc_dict.get(
                'category'),
            'number': doc_dict.get('number'),
            'image_url': doc_dict.get('image_url'),
            'description': safe_description,
            'quantity_max': doc_dict.get('quantity_max'),
            'price': doc_dict.get('price'),
            'stone': doc_dict.get('stone'),
            'plating': _(doc_dict.get('plating')),
            'material': _(doc_dict.get('material')),
            'sum': str(round(doc_dict.get('price') * doc_dict.get('quantity'), 1))
        }
        cart.append(cart_item)

    return cart


def getCart(request):
    return JsonResponse({'cart': get_cart(get_user_session_type(request))})


def get_stones():
    docs = stones_ref.stream()

    # Преобразование данных в объект { "id": "name" }
    stones = {}
    for doc in docs:
        data = doc.to_dict()
        if 'id' in data and 'name' in data:
            stones[data['id']] = data['name']

    return stones


def update_quantity_input(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            product_id = data.get('product_id')
            quantity_new = data.get('quantity_new')
            price = float(data.get('price'))
            email = get_user_session_type(request)  # Replace with actual user email

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
                    'stone': str(product['stone']),
                    'material': product['material'],
                    'plating': product['plating'],
                    "emailOwner": email,
                    'image_url': product['image-url'],
                    "name": product['name'],
                    "price": price,
                    "quantity": quantity_new,
                    "number": number_in_cart,
                    "product_name": product['product_name'],
                    "category": product['category'],
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
            email = get_user_session_type(request)
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
        'ActivePromocodes': 'email',
        'Addresses': 'email',
    }

    old_coupon = get_active_coupon(old_email)
    new_coupon = get_active_coupon(new_email)

    if new_coupon:
        delete_user_coupons(old_email)

    old_discount = old_coupon.get('discount', 0) / 100.0 if old_coupon else 0
    new_discount = new_coupon.get('discount', 0) / 100.0 if new_coupon else 0

    # Loop through the mapping
    for collection_name, email_field in collection_email_fields.items():
        try:
            # Reference the collection
            collection_ref = db.collection(collection_name)
            # Query for documents with the old email
            docs_to_update = collection_ref.where(email_field, '==', old_email).get()
            # Update each document with the new email
            for doc in docs_to_update:
                doc_data = doc.to_dict()

                # Если коллекция — это Cart, пересчитаем цены
                if collection_name == 'Cart' and 'price' in doc_data:
                    original_price = doc_data['price']
                    # Восстанавливаем изначальную цену, если есть скидка старого купона
                    if old_discount > 0:
                        if new_discount > 0:
                            original_price = original_price / (1 - old_discount)

                    # Применяем новую скидку, если есть новый купон
                    if new_discount > 0:
                        updated_price = original_price * (1 - new_discount)
                    else:
                        updated_price = original_price

                    # Обновляем цену в документе
                    doc.reference.update({
                        'price': updated_price
                    })

                # Обновляем email в документе
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
    if feature_name == "manage_banners":
        if request.method == "POST":
            form = BannerForm(request.POST, request.FILES)
            if form.is_valid():
                new_banner = form.save(commit=False)
                new_banner.priority = Banner.objects.count()
                new_banner.save()
                return redirect('admin_tools', feature_name='manage_banners')
    # Banner.objects.all().delete()
    email = request.user.email
    form = BannerForm()
    special = False
    if email == "specialAdmin@oliverweber.at":  # TODO: HERE I HAVE TO PASTE EMAIL OF SPECIAL ADMIN
        special = True
    banners = Banner.objects.all().order_by('priority')
    print(Banner.objects.all())
    context = {
        "feature_name": feature_name,
        'banners': banners,
        'form': form,
        'special': special
    }
    if feature_name == "manage_promocodes":
        context['promocodes'] = get_promo_codes()
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


def fetch_document_name(item):
    if isinstance(item, str):
        item_ref = db.document(item)
    else:
        item_ref = item  # Assuming it's a document reference already
    doc = item_ref.get()
    return doc.to_dict() if doc.exists else None


def parallel_fetch_names(item_list):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        order_items_dict = list(executor.map(fetch_document_name, item_list))

    items = {}
    for item in order_items_dict:
        items[item.get("name")] = item
    return items


def process_items(item_list):
    """ Process items from item list with efficient fetching and error handling. """
    all_orders = parallel_fetch_names(item_list)

    names = [item for item in all_orders.keys()]

    # assuming item_list consists of item names
    name_to_item_data = fetch_items_by_names(names)
    order_items = []
    for name in names:
        item_data = name_to_item_data.get(name)
        if item_data and 'quantity' in item_data and 'price' in item_data:
            order_items.append({
                **all_orders.get(name),
                'quantity_max': item_data.get('quantity'),  # Example additional data
                'total': round(all_orders.get(name)['quantity'] * all_orders.get(name).get('price', 0), 2)
            })
    return order_items


def fetch_items_by_names(names):
    """ Fetch items by names using batched 'IN' queries to reduce the number of read operations. """
    items_ref = db.collection('item')
    name_to_item_data = {}

    # Firestore supports up to 10 items in an 'IN' query
    for i in range(0, len(names), 10):
        batch_names = names[i:i + 10]
        query_result = items_ref.where('name', 'in', batch_names).get()
        for doc in query_result:
            if doc.exists:
                name_to_item_data[doc.get('name')] = doc.to_dict()
    return name_to_item_data


def get_order(order_id):
    # Ищем по ключу `order_id`
    chosenOrderRef = orders_ref.where("order_id", '==', int(order_id)).limit(1).stream()
    order = {}

    for chosenReference in chosenOrderRef:
        order = chosenReference.to_dict()
        break  # Если найден хотя бы один результат, выходим из цикла

    # Если ничего не найдено, ищем по ключу `order-id`
    if not order:
        chosenOrderRef = orders_ref.where("`order-id`", '==', int(order_id)).limit(1).stream()
        for chosenReference in chosenOrderRef:
            order = chosenReference.to_dict()
            break  # Если найден хотя бы один результат, выходим из цикла

    return order


def get_order_items(order_id):
    chosenOrderRef = orders_ref.where("`order-id`", '==', int(order_id)).limit(1).stream()
    specificOrderData = {}

    for chosenReference in chosenOrderRef:
        specificOrderData = chosenReference.to_dict()

    # Assuming you have a way to reference your 'Item' collection
    itemList = specificOrderData.get('list', [])

    order_items = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(process_items, itemList)
        try:
            order_items = future.result(timeout=30)  # Adding a generous timeout to see if it helps
        except Exception as e:
            print(f"Unhandled exception: {e}")
    return order_items


def get_promo_codes():
    promocodes = promocodes_ref.stream()
    promocodes_data = []

    for promocode in promocodes:
        promocodes_data.append(promocode.to_dict())

    return promocodes_data


def get_active_coupon(email):
    query = active_promocodes_ref.where('email', '==', email).limit(1).stream()

    # Получаем первый купон, если он существует
    active_coupon = next(query, None)

    if active_coupon:
        coupon_data = active_coupon.to_dict()

        # Удаляем поля, если они присутствуют
        coupon_data.pop('created_at', None)
        coupon_data.pop('expires_at', None)

        return coupon_data
    else:
        return {}

def active_cart_coupon(email):
    try:
        # Проверяем, есть ли активный купон для пользователя
        active_coupons = list(active_promocodes_ref.where('email', '==', email).stream())

        if not active_coupons:
            return JsonResponse({'status': 'error', 'message': 'No active coupons for the user'})

        # Предполагаем, что только один купон активен (берём первый)
        active_coupon = active_coupons[0].to_dict()
        discount = active_coupon.get('discount', 0)

        if not isinstance(discount, (int, float)) or discount <= 0:
            return JsonResponse({'status': 'error', 'message': 'Invalid active coupon'})

        discount_rate = 1 - (discount / 100.0)

        # Применяем скидку к товарам в корзине
        docs = cart_ref.where('emailOwner', '==', email).stream()

        updated_cart = []
        for doc in docs:
            doc_dict = doc.to_dict()

            if 'price' in doc_dict and isinstance(doc_dict['price'], (int, float)):
                # Применяем скидку к цене
                new_price = doc_dict['price'] * discount_rate

                # Обновляем документ в Firestore
                cart_ref.document(doc.id).update({'price': new_price})
                doc_dict['price'] = new_price  # Обновляем локально для возвращения данных

            updated_cart.append(doc_dict)

        return JsonResponse({
            'status': 'success',
            'message': 'Discount applied to cart items',
            'updated_cart': updated_cart
        })

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'Error applying coupon: {str(e)}'})

def delete_user_coupons(email):
    try:
        # Ищем все активные купоны пользователя
        user_coupons = active_promocodes_ref.where('email', '==', email).stream()

        # Удаляем каждый купон
        for coupon in user_coupons:
            active_promocodes_ref.document(coupon.id).delete()

        return {"status": "success", "message": "All active coupons for the user have been deleted"}

    except Exception as e:
        return {"status": "error", "message": f"An error occurred: {str(e)}"}