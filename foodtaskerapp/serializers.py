from rest_framework import serializers

from .models import Restaurant


class RestaurantSerializer(serializers.ModelSerializer):
    logo = serializers.SerializerMethodField()

    def get_logo(self, restaurant):
        request = self.context.get('request')
        logo_urls = restaurant.logo.url
        return request.build_absolute_uri(logo_urls)

    class Meta:
        model = Restaurant
        fields = ('id', 'name', 'phone', 'address', 'logo')