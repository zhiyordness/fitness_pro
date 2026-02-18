from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import DetailView, CreateView, UpdateView, DeleteView, ListView


from nutrition.forms import MealForm
from nutrition.models import Meal, MealFoodItem, NutritionDay


class NutritionCalculator:

    @staticmethod
    def calculate_meal_totals(meal: Meal) -> dict:
        totals = {
            'calories': 0,
            'protein': 0,
            'carbohydrates': 0,
            'fat': 0
        }

        for item in meal.mealfooditem_set.all():
            totals['calories'] += item.food.calories * item.quantity
            totals['protein'] += item.food.protein * item.quantity
            totals['carbohydrates'] += item.food.carbohydrates * item.quantity
            totals['fat'] += item.food.fat * item.quantity
        return totals

    @staticmethod
    def calculate_day_totals(day):
        totals = {
            'calories': 0,
            'protein': 0,
            'carbohydrates': 0,
            'fat': 0,
        }

        for meal in day.meals.all():
            meal_totals = NutritionCalculator.calculate_meal_totals(meal)
            for key in totals:
                totals[key] += meal_totals[key]

        return totals

class NutritionHomeView(ListView):
    model = NutritionDay
    template_name = 'nutrition/nutrition-overview.html'
    context_object_name = 'days'

    def get_queryset(self):
        return NutritionDay.objects.prefetch_related(
            'meals',
            'meals__mealfooditem_set',
            'meals__mealfooditem_set__food'
        ).all()

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)

        days = self.get_queryset()

        day_totals = {}
        for day in days:
            day_totals[day.pk] = NutritionCalculator.calculate_day_totals(day)

        meals = Meal.objects.prefetch_related(
            'mealfooditem_set__food',
        ).all().order_by('time')


        for meal in meals:
            meal.totals = NutritionCalculator.calculate_meal_totals(meal)


        context['days'] = days
        context['day_totals'] = day_totals
        context['meals'] = meals
        context['meal_items'] = MealFoodItem.objects.select_related('food').all()

        return context



class PlanDetailsView(DetailView):
    model = Meal
    template_name = 'nutrition/plan-details.html'
    context_object_name = 'plan'
    http_method_names = ['get']

    def get_success_url(self):
        return reverse_lazy('nutrition:plan-details', kwargs={'pk': self.object.pk})


class PlanCreateView(CreateView):
    model = Meal
    form_class = MealForm
    template_name = 'nutrition/plan/plan-create.html'

    def form_valid(self, form):
        messages.success(self.request, 'Meal Plan has been created successfully!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('nutrition:plan-details', kwargs={'pk': self.object.pk})



class PlanEditView(UpdateView):
    model = Meal
    form_class = MealForm
    template_name = 'nutrition/plan/plan-edit.html'

    def form_valid(self, form):
        messages.success(self.request, 'Meal Plan has been updated successfully!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('nutrition:plan-details', kwargs={'pk': self.object.pk})



class PlanDeleteView(DeleteView):
    model = Meal
    template_name = 'nutrition/plan/plan-delete.html'


    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Meal Plan has been deleted successfully!')
        return super().delete(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('nutrition:day-details', kwargs={'pk': self.object.pk})




def meal_details(request: HttpRequest, pk: int) -> HttpResponse:
    return render(request, 'nutrition/meal/meal-details.html')


def meal_create(request: HttpRequest) -> HttpResponse:
    return render(request, 'nutrition/meal/meal-create.html')


def meal_edit(request: HttpRequest, pk: int) -> HttpResponse:
    return render(request, 'nutrition/meal/meal-edit.html')


def meal_delete(request: HttpRequest, pk: int) -> HttpResponse:
    return render(request, 'nutrition/meal/meal-delete.html')



def item_details(request: HttpRequest, pk: int) -> HttpResponse:
    return render(request, 'nutrition/item/item-details.html')


def item_create(request: HttpRequest) -> HttpResponse:
    return render(request, 'nutrition/item/item-create.html')


def item_edit(request: HttpRequest, pk: int) -> HttpResponse:
    return render(request, 'nutrition/item/item-edit.html')


def item_delete(request: HttpRequest, pk: int) -> HttpResponse:
    return render(request, 'nutrition/item/item-delete.html')

