from django.shortcuts import render
import os
import firebase_admin
from firebase_admin import credentials, firestore
from django.conf import settings
json_file_path = os.path.join(settings.BASE_DIR,"shop", "static", "key2.json")
cred = credentials.Certificate(json_file_path)
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)
db = firestore.client()

def form_page(request):
    matched_documents = []
    search_term=''
    if request.method == 'POST':
        search_term = request.POST.get('number').lower()

        # Initialize Firebase (if not already initialized)
        # firebase_admin.initialize_app()
        documents = db.collection('item').stream()
        if search_term!='':
            # Manual filtering
            for doc in documents:
                doc_dict = doc.to_dict()
                if search_term in doc_dict.get('name', '').lower():
                    matched_documents.append(doc_dict)
    context = {
        'documents': matched_documents,
        'search_term': search_term
    }

    return render(request, 'shop_page.html', context)

# Create your views here.
