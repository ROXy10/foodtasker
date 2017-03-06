from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect

from .forms import UserForm, RestaurantForm, UserEditForm, MealForm
from .models import Meal

def home(request):
    return redirect(restaurant_home)


@login_required(login_url='/restaurant/sign-in/')
def restaurant_home(request):
    return redirect(restaurant_order)


@login_required(login_url='/restaurant/sign-in/')
def restaurant_account(request):
    user_form = UserEditForm(instance=request.user)
    restaurant_form = RestaurantForm(instance=request.user.restaurant)

    if request.method == 'POST':
        user_form = UserEditForm(request.POST, instance=request.user)
        restaurant_form = RestaurantForm(request.POST, request.FILES, instance=request.user.restaurant)

        if user_form.is_valid() and restaurant_form.is_valid():
            user_form.save()
            restaurant_form.save()

    context = {
        'user_form': user_form,
        'restaurant_form': restaurant_form,
    }
    return render(request, 'restaurant/account.html', context)


@login_required(login_url='/restaurant/sign-in/')
def restaurant_meal(request):
    meals = Meal.objects.filter(restaurant=request.user.restaurant).order_by('-id')
    context = {
        'meals': meals
    }
    return render(request, 'restaurant/meal.html', context)


@login_required(login_url='/restaurant/sign-in/')
def restaurant_add_meal(request):
    form = MealForm()
    if request.method == 'POST':
        form = MealForm(request.POST, request.FILES)

        if form.is_valid():
            meal = form.save(commit=False)
            meal.restaurant = request.user.restaurant
            meal.save()
            return redirect(restaurant_meal)

    context = {
        'form': form,
    }
    return render(request, 'restaurant/add_meal.html', context)


@login_required(login_url='/restaurant/sign-in/')
def restaurant_edit_meal(request, meal_id):
    form = MealForm(instance=Meal.objects.get(id=meal_id))
    if request.method == 'POST':
        form = MealForm(request.POST, request.FILES, instance=Meal.objects.get(id=meal_id))

        if form.is_valid():
            form.save()
            return redirect(restaurant_meal)

    context = {
        'form': form,
    }
    return render(request, 'restaurant/edit_meal.html', context)


@login_required(login_url='/restaurant/sign-in/')
def restaurant_order(request):
    context = {

    }
    return render(request, 'restaurant/order.html', context)


@login_required(login_url='/restaurant/sign-in/')
def restaurant_report(request):
    context = {

    }
    return render(request, 'restaurant/report.html', context)


def restaurant_sing_up(request):
    user_form = UserForm()
    restaurant_form = RestaurantForm()

    if request.method == 'POST':
        user_form = UserForm(request.POST)
        restaurant_form = RestaurantForm(request.POST, request.FILES)

        if user_form.is_valid() and restaurant_form.is_valid():
            new_user = User.objects.create_user(**user_form.cleaned_data)
            new_restaurant = restaurant_form.save(commit=False)
            new_restaurant.user = new_user
            new_restaurant.save()

            login(request, authenticate(
                username=user_form.cleaned_data['username'],
                password=user_form.cleaned_data['password']
            ))

            return redirect(restaurant_home)

    context = {
        'user_form': user_form,
        'restaurant_form': restaurant_form,
    }
    return render(request, 'restaurant/sign_up.html', context)