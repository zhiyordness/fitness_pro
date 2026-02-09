from datetime import date

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect

from training.models import TrainingDay


# Create your views here.

def current_training_day_details(request: HttpRequest) -> HttpResponse:
    today_name = date.today().strftime('%A')
    training_day = TrainingDay.objects.filter(day__iexact=today_name).first()
    exercises = training_day.exercises.all() if training_day else None

    context = {
        'training_day': training_day,
        'exercises': exercises,
    }

    return render(request, 'home/home-page.html', context)