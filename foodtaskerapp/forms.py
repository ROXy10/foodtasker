from django import forms
from django.contrib.auth.models import User
from django.utils import timezone

from .models import Restaurant, Meal, Order, OrderDetail


class UserForm(forms.ModelForm):
    email = forms.EmailField(max_length=100, required=True, widget=forms.EmailInput)
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = (
            'username',
            'password',
            'first_name',
            'last_name',
            'email',
        )


class UserEditForm(forms.ModelForm):
    email = forms.EmailField(max_length=100, required=True, widget=forms.EmailInput)

    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            'email',
        )


class RestaurantForm(forms.ModelForm):
    class Meta:
        model = Restaurant
        fields = (
            'name',
            'phone',
            'address',
            'logo',
        )


class MealForm(forms.ModelForm):
    class Meta:
        model = Meal
        exclude = ('restaurant',)


class OrderForm(forms.ModelForm):
    created_at = forms.DateTimeField(widget=forms.SelectDateWidget, initial=timezone.now)
    picked_at = forms.DateTimeField(widget=forms.SelectDateWidget, initial=timezone.now)

    class Meta:
        model = Order
        exclude = ('restaurant', 'attribution')
