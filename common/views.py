from nutrition.views import NutritionCalculator
from datetime import date, datetime
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.utils import timezone
from django.views import View
from nutrition.models import Meal
from progress.models import ProgresTracking
from training.models import TrainingDay



class HomePageView(View):
    template_name = 'home/home-page.html'

    def get_weight_change(self):
        weight_records = ProgresTracking.objects.all()
        if weight_records.count() >= 2:
            last_weight = weight_records.first().weight
            previous_weight = weight_records.last().weight
            return abs(last_weight - previous_weight)
        return 0


    def get(self, request, *args, **kwargs):
        today_name = date.today().strftime('%A')
        training_days = TrainingDay.objects.all()
        training_day = TrainingDay.objects.filter(day__iexact=today_name).first()

        exercises = None
        if training_day:
            exercises = training_day.exercises.all().select_related('muscles')

        now_time = datetime.now().time()
        next_meal = Meal.objects.filter(time__gte=now_time, day__name__icontains=today_name).first() or None
        if next_meal:
            meal_items = next_meal.mealfooditem_set.select_related('food').all() if next_meal else []
            total_calories = NutritionCalculator.calculate_meal_totals(next_meal)['calories']
        else:
            meal_items = []
            total_calories = 0

        today_date = timezone.now()
        weight_change = self.get_weight_change()


        context = {
            'training_days': training_days,
            'training_day': training_day,
            'exercises': exercises,
            'next_meal': next_meal,
            'meal_items': meal_items,
            'today_date': today_date,
            'weight_change': weight_change,
            'current_weight_record': ProgresTracking.objects.first(),
            'total_calories': total_calories,
        }

        return render(request, self.template_name, context)



def page_not_found_view(request: HttpRequest, exception) -> HttpResponse:
    return render(request, 'errors/404.html', status=404)