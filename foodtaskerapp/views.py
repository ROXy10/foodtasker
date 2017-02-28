from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect


def home(request):
    return redirect(restaurant_home)


@login_required(login_url='/restaurant/sign-in/')
def restaurant_home(request):
    context = {

    }
    return render(request, 'restaurant/home.html', context)