from rest_framework import serializers

from .models import Restaurant, Meal


class RestaurantSerializer(serializers.ModelSerializer):
    logo = serializers.SerializerMethodField()

    def get_logo(self, restaurant):
        request = self.context.get('request')
        logo_urls = restaurant.logo.url
        return request.build_absolute_uri(logo_urls)

    class Meta:
        model = Restaurant
        fields = ('id', 'name', 'phone', 'address', 'logo')


class MealSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    def get_image(self, meal):
        request = self.context.get('request')
        logo_urls = meal.image.url
        return request.build_absolute_uri(logo_urls)

    class Meta:
        model = Meal
        fields = ('id', 'name', 'short_description', 'image', 'price')