from django.contrib import admin
from .models import Restaurant, Customer, Driver, Meal, Order, OrderDetail


admin.site.register(Restaurant)
admin.site.register(Customer)
admin.site.register(Driver)
admin.site.register(Meal)
admin.site.register(Order)
admin.site.register(OrderDetail)