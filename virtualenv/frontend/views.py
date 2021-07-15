from django.shortcuts import render

# Create your views here.
def index(request, *args, **kwards):
    return render(request, 'frontend/index.html')