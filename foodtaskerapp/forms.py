from django import forms
from django.contrib.auth.models import User

from .models import Restaurant


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

