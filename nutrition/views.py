from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

# Create your views here.

def plan_details(request: HttpRequest, pk: int) -> HttpResponse:
    return render(request, 'nutrition/plan-details.html')


def plan_create(request: HttpRequest) -> HttpResponse:
    return render(request, 'nutrition/plan/plan-create.html')


def plan_edit(request: HttpRequest, pk: int) -> HttpResponse:
    return render(request, 'nutrition/plan/plan-edit.html')


def plan_delete(request: HttpRequest, pk: int) -> HttpResponse:
    return render(request, 'nutrition/plan/plan-delete.html')



def meal_details(request: HttpRequest, pk: int) -> HttpResponse:
    return render(request, 'nutrition/meal/meal-details.html')


def meal_create(request: HttpRequest) -> HttpResponse:
    return render(request, 'nutrition/meal/meal-create.html')


def meal_edit(request: HttpRequest, pk: int) -> HttpResponse:
    return render(request, 'nutrition/meal/meal-edit.html')


def meal_delete(request: HttpRequest, pk: int) -> HttpResponse:
    return render(request, 'nutrition/meal/meal-delete.html')



def day_details(request: HttpRequest, pk: int) -> HttpResponse:
    return render(request, 'nutrition/day/day-details.html')


def day_create(request: HttpRequest) -> HttpResponse:
    return render(request, 'nutrition/day/day-create.html')


def day_edit(request: HttpRequest, pk: int) -> HttpResponse:
    return render(request, 'nutrition/day/day-edit.html')


def day_delete(request: HttpRequest, pk: int) -> HttpResponse:
    return render(request, 'nutrition/day/day-delete.html')




def item_details(request: HttpRequest, pk: int) -> HttpResponse:
    return render(request, 'nutrition/item/item-details.html')


def item_create(request: HttpRequest) -> HttpResponse:
    return render(request, 'nutrition/item/item-create.html')


def item_edit(request: HttpRequest, pk: int) -> HttpResponse:
    return render(request, 'nutrition/item/item-edit.html')


def item_delete(request: HttpRequest, pk: int) -> HttpResponse:
    return render(request, 'nutrition/item/item-delete.html')

