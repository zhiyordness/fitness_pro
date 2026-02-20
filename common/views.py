from datetime import date, datetime

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views import View

from nutrition.models import Meal
from training.models import TrainingDay


# Create your views here.
class HomePageView(View):

    template_name = 'home/home-page.html'

    def get(self, request, *args, **kwargs):
        today_name = date.today().strftime('%A')
        training_days = TrainingDay.objects.all()
        training_day = TrainingDay.objects.filter(day__iexact=today_name).first()
        exercises = training_day.exercises.all() if training_day else None

        now_time = datetime.now().time()
        next_meal = Meal.objects.filter(time__gte=now_time).order_by('time').first()

        context = {
            'training_days': training_days,
            'training_day': training_day,
            'exercises': exercises,
            'next_meal': next_meal,
        }

        return render(request, self.template_name, context)

# def current_training_day_details(request: HttpRequest) -> HttpResponse:
#     today_name = date.today().strftime('%A')
#     training_day = TrainingDay.objects.filter(day__iexact=today_name).first()
#     exercises = training_day.exercises.all() if training_day else None
#
#     now_time = datetime.now().time()
#     next_meal = Meal.objects.filter(time__gte=now_time).order_by('time').first()
#
#     context = {
#         'training_day': training_day,
#         'exercises': exercises,
#         'next_meal': next_meal,
#     }
#
#     return render(request, 'home/home-page.html', context)


def page_not_found_view(request: HttpRequest, exception) -> HttpResponse:
    return render(request, 'errors/404.html', status=404)