from django.shortcuts import render

# Create your views here.
def index(request):
    return render(request, 'index.html')

def events(request):
    return render(request, 'events.html')