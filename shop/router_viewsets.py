import logging

import googlemaps
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from OnlineShop import settings
from shop.models import PromoCode, Store
from shop.serializers import PromoCodeSerializer, StoreSerializer
from shop.views import haversine

logger = logging.getLogger(__name__)

class PromoCodeViewSet(viewsets.ViewSet):
    def list(self, request):
        # Get a list of all promo codes
        promocodes = PromoCode.get_all()
        return Response(promocodes)

    def retrieve(self, request, pk=None):
        # Get one promo code by ID
        promocode = PromoCode.get_by_id(pk)
        if not promocode:
            return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
        return Response(promocode)

    def create(self, request):
        # Create new promo code
        serializer = PromoCodeSerializer(data=request.data)
        if serializer.is_valid():
            doc_id = PromoCode.create(serializer.validated_data)
            return Response({'id': doc_id}, status=status.HTTP_201_CREATED)
        else:
            logger.warning("Validation errors:", serializer.errors)  # Validation error log
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        # Update promo code
        serializer = PromoCodeSerializer(data=request.data)
        if serializer.is_valid():
            PromoCode.update(pk, serializer.validated_data)
            return Response({'status': 'updated'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        # Delete promo code
        PromoCode.delete(pk)
        return Response({'status': 'deleted'}, status=status.HTTP_204_NO_CONTENT)


class StoreViewSet(viewsets.ModelViewSet):
    queryset = Store.objects.all()
    serializer_class = StoreSerializer

    @action(detail=False, methods=['get'])
    def get_suggestions(self, request):
        query = request.query_params.get('query', '')
        if not query:
            return Response([])

        gmaps = googlemaps.Client(key=settings.GOOGLE_MAPS_API_KEY)
        try:
            places_autocomplete_result = gmaps.places_autocomplete(query)
            suggestions = [p['description'] for p in places_autocomplete_result]
            return Response(suggestions)
        except Exception as e:
            logger.info(e)
            return Response({'error': str(e)}, status=500)

    @action(detail=False, methods=['get'])
    def nearby(self, request):
        """
        GET /api/stores/nearby/?lat=<>&lng=<>&radius=<km>
        returns up to 5 stores within radius of (lat,lng)
        """
        address = request.query_params.get('useraddress')
        radius = request.query_params.get('radius')

        if not address or not radius:
            return Response({"detail": "address and radius are mandatory"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            gmaps = googlemaps.Client(key=settings.GOOGLE_MAPS_API_KEY)
            geocode_result = gmaps.geocode(f'{address}')
            if geocode_result and len(geocode_result) > 0:
                origin_lat = geocode_result[0]['geometry']['location']['lat']
                origin_lng = geocode_result[0]['geometry']['location']['lng']

                results = []
                for store in self.get_queryset():
                    distance = haversine(origin_lat, origin_lng, store.latitude, store.longitude)
                    if distance <= float(radius):
                        results.append({'distance_km': round(distance, 2), **StoreSerializer(store).data})

                results.sort(key=lambda x: x['distance_km'])
                nearest = results[:5]
                return Response(nearest)
            else:
                return Response({"detail": f"Сould not determine the coordinates for the address: {address}"},
                                status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({"detail": f"An error occurred during geocoding: {e}"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)