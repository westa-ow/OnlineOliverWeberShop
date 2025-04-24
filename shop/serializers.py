import googlemaps
from geopy import Nominatim
from rest_framework import serializers

from OnlineShop import settings
from shop.models import Store


class PromoCodeSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    code = serializers.CharField(max_length=50)
    type = serializers.ChoiceField(choices=['Full', 'ProductsOnly'])
    discount = serializers.IntegerField(default=0)
    expiration_date = serializers.DateField(allow_null=True, required=False)
    creation_date = serializers.DateTimeField(read_only=True)
    is_active = serializers.BooleanField(default=True)
    b2b_only = serializers.BooleanField(default=False)
    single_use = serializers.BooleanField(default=False)


class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = ['id', 'address', 'latitude', 'longitude']
        read_only_fields = ['latitude', 'longitude']

    def _geocode_address(self, address):
        """Геокодирует адрес с помощью Google Geocoding API."""
        gmaps = googlemaps.Client(key=settings.GOOGLE_MAPS_API_KEY)
        try:
            geocode_result = gmaps.geocode(address)
            if geocode_result:
                location = geocode_result[0]['geometry']['location']
                return location['lat'], location['lng']
            else:
                return None, None
        except Exception as e:
            raise serializers.ValidationError(f"Google geocoding error occurred: {e}")

    # def validate_address(self, value):
    #     """Проверяем, удалось ли геокодировать адрес."""
    #     geolocator = Nominatim(user_agent="ow_shop")
    #     try:
    #         print(value)
    #         location = geolocator.geocode(value)
    #         if location is None:
    #             raise serializers.ValidationError("Could not determine the coordinates for the specified address. Please check the correct spelling.")
    #     except Exception as e:
    #         raise serializers.ValidationError(f"Geocoding error occurred: {e}")
    #     return value

    def validate_address(self, value):
        """Проверяем, удалось ли геокодировать адрес с помощью Google."""
        latitude, longitude = self._geocode_address(value)
        if latitude is None or longitude is None:
            raise serializers.ValidationError(
                "Could not determine the coordinates for the specified address. Please check the correct spelling.")
        return value

    def create(self, validated_data):
        address = validated_data['address']
        latitude, longitude = self._geocode_address(address)
        store = Store.objects.create(
            address=address,
            latitude=latitude,
            longitude=longitude
        )
        return store

    def update(self, instance, validated_data):
        instance.address = validated_data.get('address', instance.address)
        latitude, longitude = self._geocode_address(instance.address)
        instance.latitude = latitude
        instance.longitude = longitude
        instance.save()
        return instance
