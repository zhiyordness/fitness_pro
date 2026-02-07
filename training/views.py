from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

# Create your views here.


def split_details(request: HttpRequest) -> HttpResponse:
    return render(request, 'training/training-details.html')




def split_create(request: HttpRequest) -> HttpResponse:
    return render(request, 'training/split/split-create.html')


def split_edit(request: HttpRequest) -> HttpResponse:
    return render(request, 'training/split/split-edit.html')


def split_delete(request: HttpRequest) -> HttpResponse:
    return render(request, 'training/split/split-delete.html')





def exercise_add(request: HttpRequest) -> HttpResponse:
    return render(request, 'training/split/split-add-exercise.html')


def exercise_edit(request: HttpRequest) -> HttpResponse:
    return render(request, 'training/exercise/exercise-edit.html')


def exercise_delete(request: HttpRequest) -> HttpResponse:
    return render(request, 'training/exercise/exercise-delete.html')


def exercise_details(request: HttpRequest) -> HttpResponse:
    return render(request, 'training/exercise/exercise-details.html')