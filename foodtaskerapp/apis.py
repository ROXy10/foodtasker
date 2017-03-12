from django.http import JsonResponse

from .models import Restaurant
from .serializers import RestaurantSerializer


def customer_get_restaurants(request):
    restaurants = RestaurantSerializer(
        Restaurant.objects.all().order_by('-id'),
        many=True,
        context={
            'request': request,
        }
    ).data

    context = {
        'restaurants': restaurants,
    }
    return JsonResponse(context)


def customer_get_meals(request):
    context = {
    }
    return JsonResponse(context)


def customer_add_order(request):
    context = {
    }
    return JsonResponse(context)


def customer_get_latest_order(request):
    context = {
    }
    return JsonResponse(context)
