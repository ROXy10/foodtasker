from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from .forms import UserForm, RestaurantForm


def home(request):
    return redirect(restaurant_home)


@login_required(login_url='/restaurant/sign-in/')
def restaurant_home(request):
    context = {

    }
    return render(request, 'restaurant/home.html', context)


def restaurant_sing_up(request):
    user_form = UserForm()
    restaurant_form = RestaurantForm

    context = {
        'user_form': user_form,
        'restaurant_form': restaurant_form,
    }
    return render(request, 'restaurant/sign_up.html', context)