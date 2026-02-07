from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

# Create your views here.

def progress_overview(request: HttpRequest) -> HttpResponse:
    return render(request, 'progress/progress-overview.html')



def record_create(request: HttpRequest) -> HttpResponse:
    return render(request, 'progress/record/record-create.html')


def record_details(request: HttpRequest, pk: int) -> HttpResponse:
    return render(request, 'progress/record/record-details.html')


def record_edit(request: HttpRequest, pk: int) -> HttpResponse:
    return render(request, 'progress/record/record-edit.html')


def record_delete(request: HttpRequest, pk: int) -> HttpResponse:
    return render(request, 'progress/record/record-delete.html')



