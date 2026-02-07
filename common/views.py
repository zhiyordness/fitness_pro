from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

# Create your views here.
def home_page(request: HttpRequest) -> HttpResponse:
    return render(request, 'common/../templates/home/home-page.html')