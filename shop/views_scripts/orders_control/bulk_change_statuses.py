import json

from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse

from shop.views import orders_ref, is_admin


@login_required
@user_passes_test(is_admin)  # Adjust the test as needed
def change_statuses(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            orderIds = data.get('orderIds')
            newStatus = data.get('status')

            if not orderIds or not newStatus:
                return JsonResponse({"success": False, "message": "Order IDs or status not provided"}, status=400)

            allOrders = orders_ref.get()

            # Build a dictionary with 'order-id' or 'order_id' as the key, and the document snapshot as the value
            orderDict = {}
            for order in allOrders:
                orderData = order.to_dict()
                key = str(orderData.get('order-id') or orderData.get('order_id'))
                orderDict[key] = order

            # Update the documents that need to be changed
            for orderId in orderIds:
                orderId = str(orderId)
                if orderId in orderDict:
                    orderRef = orderDict[orderId].reference
                    orderRef.update({'Status': newStatus})

            return JsonResponse({"success": True, "message": "Order statuses updated successfully."})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)