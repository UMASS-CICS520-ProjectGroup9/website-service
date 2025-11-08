from django.shortcuts import render

from .models import posts


# Create your views here.
def index(request):
    return render(request, 'index.html', { 'posts': posts })

