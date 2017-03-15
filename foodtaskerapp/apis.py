import json

from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from oauth2_provider.models import AccessToken

from .models import Restaurant, Meal, Order, OrderDetail
from .serializers import RestaurantSerializer, MealSerializer, OrderSerializer

import stripe
from foodtasker.settings import STRIPE_API_KEY


stripe.api_key = STRIPE_API_KEY


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

        # Get Stripe token
        stripe_token = request.POST['stripe_token']

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
            # Step 1 - Create a charge: this will charge customer's card
            charge = stripe.Charge.create(
                amount=order_total*100, # Amount is cents
                currency='usd',
                source=stripe_token,
                description='FoodTasker Order',
            )

            if charge.status != 'failed':
                # Step 2 - Create an Order
                order = Order.objects.create(
                    customer=customer,
                    restaurant_id=request.POST['restaurant_id'],
                    total=order_total,
                    status=Order.COOKING,
                    address=request.POST['address']
                )

                # Step 3 - Create order details
                for meal in order_details:
                    OrderDetail.objects.create(
                        order=order,
                        meal_id=meal['meal_id'],
                        quantity=meal['quantity'],
                        sub_total=Meal.objects.get(id=meal['meal_id']).price * meal['quantity']
                    )

                return JsonResponse({'status': 'success'})
            else:
                return JsonResponse({'status': 'failed', 'error': 'Failed connect to Stripe.'})


def customer_get_latest_order(request):
    access_token = AccessToken.objects.get(token=request.GET.get('access_token'), expires__gt=timezone.now())
    customer = access_token.user.customer
    order = OrderSerializer(Order.objects.filter(customer=customer).last()).data

    context = {
        'order': order
    }
    return JsonResponse(context)


def customer_driver_location(request):
    access_token = AccessToken.objects.get(token=request.GET.get('access_token'), expires__gt=timezone.now())
    customer = access_token.user.customer

    # Get driver's location related to this customer's currents order.
    current_order = Order.objects.filter(customer=customer, status=Order.ONTHEWAY).last()
    location = current_order.driver.location

    context = {
        'location': location
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


@csrf_exempt
def driver_pick_order(request):
    """
        POST
        :param:
            access_token
            order_id
    """
    if request.method == 'POST':
        # Get token
        access_token = AccessToken.objects.get(token=request.POST.get('access_token'), expires__gt=timezone.now())

        #Get driver
        driver = access_token.user.driver

        # Check if driver can only pick up one order at the same time
        if Order.objects.filter(driver=driver).exclude(status=Order.ONTHEWAY):
            context = {
                'status': 'failed',
                'error': 'Tou can only pick one order at the same time.'
            }
            return JsonResponse(context)

        try:
            order = Order.objects.get(id=request.POST['order_id'], driver=None, status=Order.READY)
            order.driver = driver
            order.status = Order.ONTHEWAY
            order.picked_at = timezone.now()
            order.save()

            context = {
                'status': 'success'
            }
            return JsonResponse(context)
        except Order.DoesNotExist:
            context = {
                'status': 'failed',
                'error': 'This order has been picked up by another.'
            }
            return JsonResponse(context)

    context = {
    }
    return JsonResponse(context)


def driver_get_latest_order(request):
    """
        GET
        :param:
            access_token
    """
    access_token = AccessToken.objects.get(token=request.GET.get('access_token'), expires__gt=timezone.now())
    driver = access_token.user.driver
    order = OrderSerializer (
        Order.objects.filter(driver=driver).order_by('picked_at').last()
    ).data

    context = {
        'order': order
    }
    return JsonResponse(context)


@csrf_exempt
def driver_complete_order(request):
    """
        POST
        :param:
            access_token
            order_id
    """
    access_token = AccessToken.objects.get(token=request.POST.get('access_token'), expires__gt=timezone.now())
    driver = access_token.user.driver
    order = Order.objects.get(id=request.POST['order_id'], driver=driver)
    order.status = Order.DELIVERED
    order.save()

    context = {
        'status': 'success'
    }
    return JsonResponse(context)


def driver_get_revenue(request):
    """
        GET
        :param:
            access_token
    """
    access_token = AccessToken.objects.get(token=request.GET.get('access_token'), expires__gt=timezone.now())
    driver = access_token.user.driver

    from datetime import timedelta

    revenue = {}
    today = timezone.now()
    current_weekdays = [today + timedelta(days=i) for i in range(0 - today.weekday(), 7 - today.weekday())]

    for day in current_weekdays:
        orders = Order.objects.filter(driver=driver,
                                     status=Order.DELIVERED,
                                     created_at__year=day.year,
                                     created_at__month=day.month,
                                     created_at__day=day.day)
        revenue[day.strftime('%a')] = sum(order.total for order in orders)

    context = {
        'revenue': revenue
    }
    return JsonResponse(context)


@csrf_exempt
def driver_update_location(request):
    """
        POST
        :param:
            access_token
            'lat, lng'
    """
    if request.method == 'POST':
        access_token = AccessToken.objects.get(token=request.POST.get('access_token'), expires__gt=timezone.now())
        driver = access_token.user.driver

        # Sel location string => database
        driver.location = request.POST['location']
        driver.save()

        context = {
            'status': 'success'
        }
        return JsonResponse(context)


