from django.http import JsonResponse

from .models import Restaurant
from .serializers import RestaurantSerializer


def customer_get_restaurant(request):
    restaurants = RestaurantSerializer(
        Restaurant.objects.all().order_by('-id'),
        many=True
    ).data

    context = {
        'restaurants': restaurants,
    }
    return JsonResponse(context)


