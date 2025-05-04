import csv
from io import BytesIO

import requests
from PIL import Image as PILImage
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse

from shop.views import is_admin, \
    orders_ref, db, get_order_items, single_order_ref, get_order
from shop.views_scripts.checkout_cart_views import make_pdf


@login_required
def download_csv_order(request, order_id):
    order_items = get_order_items(order_id)
    # Prepare response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="order_{order_id}.csv"'.format(order_id)

    writer = csv.writer(response)
    writer.writerow(['product_number', 'quantity', 'price', 'total'])  # Writing the headers

    # Assuming 'list' contains the items in the order with 'name', 'quantity', 'price'
    for item in order_items:
        product_number = item.get('name')
        quantity = item.get('quantity')
        price = item.get('price')
        total = item.get('total')
        writer.writerow([product_number, quantity, price, total])

    return response

@login_required
def download_pdf_no_img(request, order_id):

    buffer = BytesIO()
    order = get_order(order_id)
    make_pdf(order, buffer, False)

    # Preparing response
    pdf = buffer.getvalue()
    buffer.close()
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="pdf_order_{order_id}_without_images.pdf"'
    response.write(pdf)

    return response


def get_optimized_image(url, output_size=(50, 50)):
    response = requests.get(url)
    image = PILImage.open(BytesIO(response.content))
    if image.mode == 'RGBA':
        image = image.convert('RGB')
    byte_io = BytesIO()
    image.save(byte_io, 'JPEG')
    byte_io.seek(0)
    return byte_io


@login_required
# @user_passes_test(is_admin)
def download_pdf_w_img(request, order_id):
    buffer = BytesIO()
    order = get_order(order_id)
    make_pdf(order, buffer, True)

    # Preparing response
    pdf = buffer.getvalue()
    buffer.close()

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="pdf_order_{order_id}_with_images.pdf"'
    response.write(pdf)

    return response

def delete_documents_in_batches(query_snapshot):
    batch = db.batch()
    count = 0

    for doc in query_snapshot:
        batch.delete(doc.reference)
        count += 1
        # Commit the batch every 500 deletes
        if count % 500 == 0:
            batch.commit()
            batch = db.batch()

    # Commit any remaining deletes in the batch
    if count % 500 != 0:
        batch.commit()

@login_required
@user_passes_test(is_admin)
def at_delete_order(request, order_id):
    order_id = int(order_id)
    orders_query = orders_ref.where('order_id', '==', order_id).get()
    if not orders_query:
        orders_query = orders_ref.where("`order-id`", '==', order_id).get()
    delete_documents_in_batches(orders_query)

    # Query and batch delete from "Order"
    order_items_query = single_order_ref.where('order_id', '==', order_id).get()
    if not order_items_query:
        order_items_query = single_order_ref.where("`order-id`", '==', order_id).get()
    delete_documents_in_batches(order_items_query)
    return HttpResponse(status=204)