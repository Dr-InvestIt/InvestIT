from django.urls import path
from .views import *

urlpatterns = [
    path('', ListStockView.as_view()), 
    path('add', CreateStockView.as_view())
]
 