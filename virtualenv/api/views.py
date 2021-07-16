from django.shortcuts import render
from django.http import HttpResponse
from rest_framework import generics, status
from .serializers import StockSerializer
from .models import Stock
from rest_framework.views import APIView
from rest_framework.response import Response


# Create your views here.
def main(request):
    return(HttpResponse("<h1>main</h1>"))

class CreateStockView(generics.CreateAPIView):
    queryset = Stock.objects.all()
    serializer_class = StockSerializer

class ListStockView(generics.ListAPIView):
    queryset = Stock.objects.all()
    serializer_class = StockSerializer