import json

from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from oauth2_provider.models import AccessToken

from .models import Restaurant, Meal, Order, OrderDetail
from .serializers import RestaurantSerializer, MealSerializer, OrderSerializer


#################
# CUSTOMERS
#################

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


def customer_get_meals(request, restaurant_id):
    meals = MealSerializer(
        Meal.objects.filter(restaurant_id=restaurant_id).order_by('-id'),
        many=True,
        context={
            'request': request,
        }
    ).data

    context = {
        'meals': meals,
    }
    return JsonResponse(context)


@csrf_exempt
def customer_add_order(request):
    """
    :param:
        access_token
        restaurant_id
        address
        order_details (json format), example:
            [{"meal_id": 2, "quantity": 2}, {"meal_id": 3, "quantity": 3}]
        stripe_token
    :return:
        {'status': 'success'}
    """
    if request.method == 'POST':
        # Get token
        access_token = AccessToken.objects.get(token=request.POST.get('access_token'), expires__gt=timezone.now())

        # Get profile
        customer = access_token.user.customer

        # Check whether customer has any order that is not delivered
        if Order.objects.filter(customer=customer).exclude(status=Order.DELIVERED):
            return JsonResponse({'status': 'failed', 'error': 'Your last order must be completed.'})

        # Check address
        if not request.POST['address']:
            return JsonResponse({'status': 'failed', 'error': 'Address is required'})

        # Get Order Detail
        order_details = json.loads(request.POST['order_details'])

        order_total = 0
        for meal in order_details:
            order_total += Meal.objects.get(id=meal['meal_id']).price * meal['quantity']

        if len(order_details) > 0:
            # Step 1 - Create an Order
            order = Order.objects.create(
                customer=customer,
                restaurant_id=request.POST['restaurant_id'],
                total=order_total,
                status=Order.COOKING,
                address=request.POST['address']
            )

            # Step 2 - Create order details
            for meal in order_details:
                OrderDetail.objects.create(
                    order=order,
                    meal_id=meal['meal_id'],
                    quantity=meal['quantity'],
                    sub_total=Meal.objects.get(id=meal['meal_id']).price * meal['quantity']
                )

            return JsonResponse({'status': 'success'})


def customer_get_latest_order(request):
    access_token = AccessToken.objects.get(token=request.GET.get('access_token'), expires__gt=timezone.now())
    customer = access_token.user.customer
    order = OrderSerializer(Order.objects.filter(customer=customer).last()).data

    context = {
        'order': order
    }
    return JsonResponse(context)


#################
# RESTAURANT
#################

def restaurant_order_notification(request, last_request_time):
    notification = Order.objects.filter(restaurant=request.user.restaurant, created_at__gt=last_request_time).count()

    context = {
        'notification': notification,
    }
    return JsonResponse(context)


#################
# DRIVERS
#################

def driver_get_ready_orders(request):
    orders = OrderSerializer(
        Order.objects.filter(status=Order.READY, driver=None).order_by('-id'),
        many=True
    ).data

    context = {
        'orders': orders,
    }
    return JsonResponse(context)


def driver_pick_order(request):

    context = {
    }
    return JsonResponse(context)


def driver_get_latest_order(request):

    context = {
    }
    return JsonResponse(context)


def driver_complete_order(request):

    context = {
    }
    return JsonResponse(context)


def driver_get_revenue(request):

    context = {
    }
    return JsonResponse(context)


