from django.http import JsonResponse
from django.shortcuts import render

from shop.decorators import login_required_or_session
from shop.views import itemsRef, get_cart, get_user_info, get_user_session_type, get_user_prices, \
    get_vocabulary_product_card, get_stones, \
    get_user_sale


@login_required_or_session
def form_page(request, product_id):
    """
    This function renders the form page for a specific product.
    """
    search_term = ''
    search_type = request.POST.get('search_type', 'default')
    email = get_user_session_type(request)
    category, currency = get_user_prices(request, email)
    stones = get_stones()
    info = get_user_info(email) or {}
    sale = get_user_sale(info)
    show_quantities = info.get("show_quantities", False)
    cart = get_cart(email)

    # Set currency symbol
    if currency == "Euro":
        currency = "€"
    elif currency == "Dollar":
        currency = "$"

    # Fetch documents
    documents = itemsRef.where('name', '==', product_id).stream()
    products = [
        {key: value for key, value in doc.to_dict().items() if key != 'Visible'}
        for doc in documents
        if (
                search_type != 'archived' or doc.to_dict().get('quantity', 0) > 0
        )
    ]

    # If no product is found, return with an is_available flag as False
    if not products:
        return render(request, 'shop_page.html', {
            "is_available": False
        })

    # Adjust price based on user category
    for obj in products:
        obj['stone'] = stones.get(obj['stone'], obj['stone'])
        if category == "VK3":
            obj['price'] = obj['priceVK3']
        elif category == "GH":
            obj['price'] = obj['priceGH']
        elif category == "Default_High":
            obj['price'] = obj['priceVK4'] * 1.3
        elif category == "USD_GH":
            obj['price'] = obj['priceUSD_GH']
        elif category == "Default_USD":
            obj['price'] = round(obj['priceUSD'] * (1 - sale), 1)
        else:
            obj['price'] = round(obj['priceVK4'] * (1 - sale), 1)

    document = products[0]
    if document.get('additionalImages'):
        document['additionalImages'] = [document.get('image_url')] + document['additionalImages']
    print(document)
    # Non-AJAX requests will return the rendered HTML page
    return render(request, 'shop_page.html', {
        'search_term': search_term,
        'cart': cart,
        'currency': currency,
        'document': document,
        'show_quantities': show_quantities,
        'product_id': product_id,
        'vocabulary': get_vocabulary_product_card(),
        'is_available': True
    })


def fetch_numbers(request):
    """
    This function fetches the numbers for the given search parameter which supposed to be product ID.
    """

    search_term = request.GET.get('term', '')
    search_type = request.GET.get('search_type', 'default')
    results = []

    if search_term != '':
        # Perform two separate queries to search by 'name' and 'product_name'
        # (case-insensitive search is applied in Python)

        raw = request.GET.get('term', '')
        low = raw.lower()
        formatted = low[:1].upper() + low[1:]
        name_query = itemsRef.where('name', '>=', formatted).where('name', '<=', formatted + '\uf8ff').stream()
        product_name_query = itemsRef.where('product_name', '>=', formatted).where('product_name', '<=',
                                                                                     formatted + '\uf8ff').stream()

        # Combine the results of both queries
        combined_docs = list(name_query) + list(product_name_query)

        # Remove duplicates if a document matches both queries
        seen_ids = set()
        results = [
            {
                'name': doc.to_dict().get('name', ''),
                'product_name': doc.to_dict().get('category', '') + " " + str(doc.to_dict().get('product_name', '')),
                'image_url': doc.to_dict().get('image_url', '')
            }
            for doc in combined_docs
            if doc.id not in seen_ids and not seen_ids.add(doc.id) and  # This ensures no duplicate documents
               (
                       search_term.lower() in doc.to_dict().get('name', '').lower() or
                       search_term.lower() in doc.to_dict().get('product_name', '').lower()
               ) 
               and doc.to_dict().get('Visible', True) and (  # Assumes default is True if 'Visible' is not present
                    search_type != 'archived' or doc.to_dict().get('quantity', 0) > 0
               )
        ]

    return JsonResponse(results, safe=False)
