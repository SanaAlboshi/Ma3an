from django.shortcuts import render
from django.http import HttpRequest
from agency.models import Tour  

def home_view(request: HttpRequest):
    tours = Tour.objects.all().order_by('-start_date')[:6]
    
    return render(request, "main/home.html", {"tours": tours})