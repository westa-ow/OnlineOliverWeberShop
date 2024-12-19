from rest_framework import serializers


class PromoCodeSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    code = serializers.CharField(max_length=50)
    type = serializers.ChoiceField(choices=['Full', 'ProductsOnly'])
    discount = serializers.IntegerField(default=0)
    expiration_date = serializers.DateField(allow_null=True, required=False)
    creation_date = serializers.DateTimeField(read_only=True)
    is_active = serializers.BooleanField(default=True)
    b2b_only = serializers.BooleanField(default=False)
