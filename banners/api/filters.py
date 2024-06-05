from django_filters import rest_framework as filters
from .models import *

class OrderModelFilter(filters.FilterSet):
    class Meta:
        model = OrderModel
        fields = ['company']
