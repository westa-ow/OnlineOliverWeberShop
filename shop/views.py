import ast

from django.shortcuts import render
import os
import json
import firebase_admin
from firebase_admin import credentials, firestore
from django.conf import settings
from django.http import JsonResponse
json_file_path = os.path.join(settings.BASE_DIR,"shop", "static", "key2.json")
cred = credentials.Certificate(json_file_path)
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)
db = firestore.client()

def form_page(request):
    documents = []
    search_term=''
    if request.method == 'POST':
        search_term = request.POST.get('number').upper()

        db = firestore.client()
        query = db.collection('item').where('name', '==', search_term)
        documents = query.stream()

    cart = get_cart()
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
        'quantity':quantity
    }

    return render(request, 'shop_page.html', context)
def fetch_numbers(request):
    search_term = request.GET.get('term', '').lower()
    numbers = []

    if search_term != '':
        # Using Firestore query to filter documents
        query = db.collection('item').where('name', '>=', search_term).where('name', '<=',
                                                                             search_term + '\uf8ff').stream()

        # Extracting names in a single loop
        numbers = [doc.to_dict().get('name', '') for doc in query if
                   search_term in doc.to_dict().get('name', '').lower()]

    return JsonResponse(numbers, safe=False)
# Create your views here.
def add_to_cart(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        product = ast.literal_eval(data.get('document'))

        email = "eramcheg@gmail.com"  # Replace with actual user email
        quantity = 1  # Replace with actual quantity
        price = product['price']  # Replace with actual price
        name = product['name']  # Replace with actual product name
        image = product['image-url']
        description = product['description']

        cart_ref = db.collection("Cart")
        new_cart_item = {
            'description':description,
            "emailOwner": email,
            'image-url': image,
            "name": name,
            "price": price,
            "quantity": quantity,
        }
        cart_ref.add(new_cart_item)

        return JsonResponse({'status': 'success', 'quantity': quantity})
    return JsonResponse({'status': 'error'}, status=400)
def update_quantity(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        product_id = data.get('product_id')
        quantity_change = data.get('quantity_change')  # Will be 1 or -1


        cart_ref = db.collection('Cart')

        # Get current quantity and update
        docs = cart_ref.where('emailOwner', '==', "eramcheg@gmail.com").where('name', '==', product_id).limit(1).stream()
        for doc in docs:
            current_quantity = doc.to_dict().get('quantity', 0)
            new_quantity = max(current_quantity + quantity_change, 1)  # Ensure quantity doesn't go below 0

            # Update the quantity in Firestore
            doc.reference.update({'quantity': new_quantity})

            return JsonResponse({'status': 'success', 'quantity': new_quantity})
        else:
            return JsonResponse({'status': 'error', 'message': 'Product not found'}, status=404)

    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)
def get_cart():
    # Access the Firebase database

    cart_ref = db.collection('Cart')

    # Get all the documents
    docs = cart_ref.where('emailOwner', '==', "eramcheg@gmail.com").stream()

    cart = []
    for doc in docs:
        cart.append({'name':doc.to_dict().get('name'),'quantity':doc.to_dict().get('quantity'),})
    return cart
def deleteProduct(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        name = data.get('document_id')
        cart_ref = db.collection('Cart')
        docs = cart_ref.where('emailOwner', '==', "eramcheg@gmail.com").where('name', '==', name).stream()
        for doc in docs:
            doc.reference.delete()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)