from django.shortcuts import render
from django.http import HttpResponse
from rest_framework import generics
from .serializers import StockSerializer
from .models import Stock

# Create your views here.
def main(request):
    return(HttpResponse("<h1>main</h1>"))

class CreateStockView(generics.CreateAPIView):
    queryset = Stock.objects.all()
    serializer_class = StockSerializer

class ListStockView(generics.ListAPIView):
    queryset = Stock.objects.all()
    serializer_class = StockSerializer