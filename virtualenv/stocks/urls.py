from django.urls import path
from . import views

urlpatterns = [
    path('', views.index_view),
    path('frontier', views.stock_create_efficient_frontier_view),
    path('volatility', views.stock_create_volatility_view)
]
