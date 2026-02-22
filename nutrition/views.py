from decimal import Decimal
from django.contrib import messages
from django.db.models import When, Case, IntegerField
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import DetailView, CreateView, UpdateView, DeleteView, ListView
from choices import WeekDaysChoices
from nutrition.forms import MealForm, MealFoodItemForm
from nutrition.models import Meal, MealFoodItem, NutritionDay, FoodDatabase


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

            item_quantity = 0
            if item.measure == 'Gr.':
                item_quantity = item.quantity / 100
            else:
                item_quantity = item.quantity

            totals['calories'] += item.food.calories * Decimal(item_quantity)
            totals['protein'] += item.food.protein * Decimal(item_quantity)
            totals['carbohydrates'] += item.food.carbohydrates * Decimal(item_quantity)
            totals['fat'] += item.food.fat * Decimal(item_quantity)
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
    paginate_by = 1

    def get_queryset(self):
        order_days = [
            When(name=WeekDaysChoices.MONDAY, then=1),
            When(name=WeekDaysChoices.TUESDAY, then=2),
            When(name=WeekDaysChoices.WEDNESDAY, then=3),
            When(name=WeekDaysChoices.THURSDAY, then=4),
            When(name=WeekDaysChoices.FRIDAY, then=5),
            When(name=WeekDaysChoices.SATURDAY, then=6),
            When(name=WeekDaysChoices.SUNDAY, then=7),
        ]
        return NutritionDay.objects.annotate(
            days_order=Case(*order_days, output_field=IntegerField())
        ).order_by('days_order').prefetch_related(
            'meals',
            'meals__mealfooditem_set',
            'meals__mealfooditem_set__food'
        ).all()

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        days = context['days']
        day_totals = {}

        for day in days:
            ordered_meals = day.meals.all()
            for meal in ordered_meals:
                meal.totals = NutritionCalculator.calculate_meal_totals(meal)
            day_totals[day.pk] = NutritionCalculator.calculate_day_totals(day)
            day.ordered_meals = ordered_meals

        context['day_totals'] = day_totals

        return context


class MealDetailsView(DetailView):
    model = Meal
    form_class = MealForm
    template_name = 'nutrition/meal/meal-details.html'
    context_object_name = 'meal'
    http_method_names = ['get']

    def get_success_url(self):
        return reverse_lazy('nutrition:nutrition-home')


class MealCreateView(CreateView):
    model = Meal
    form_class = MealForm
    template_name = 'nutrition/meal/meal-create.html'

    def form_valid(self, form):
        day = get_object_or_404(NutritionDay, pk=self.kwargs['day_pk'])
        form.instance.day = day
        messages.success(self.request, 'The Meal has been created successfully!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('nutrition:day-details', kwargs={'pk': self.object.day.pk})


class MealEditView(UpdateView):
    model = Meal
    form_class = MealForm
    template_name = 'nutrition/meal/meal-edit.html'

    def form_valid(self, form):
        messages.success(self.request, 'The meal has been updated successfully!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('nutrition:day-details',kwargs={'pk': self.object.day.pk})


class MealDeleteView(DeleteView):
    model = Meal
    template_name = 'nutrition/meal/meal-delete.html'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'The meal has been deleted successfully!')
        return super().delete(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('nutrition:day-details',kwargs={'pk': self.object.day.pk})


class ItemAddView(CreateView):
    model = MealFoodItem
    form_class = MealFoodItemForm
    template_name = 'nutrition/item/item-add.html'

    def dispatch(self, request, *args, **kwargs):
        self.meal = get_object_or_404(Meal, pk=self.kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.meal = self.meal
        messages.success(self.request, 'The item has been created successfully!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('nutrition:day-details', kwargs={'pk': self.meal.day.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['meal'] = self.meal
        return context


class ItemDeleteView(DeleteView):
    model = MealFoodItem
    template_name = 'nutrition/item/item-delete.html'
    context_object_name = 'item'

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy(
            'nutrition:day-details',
            kwargs={'pk': self.object.meal.day.pk}
        )


class DayDetailsView(DetailView):
    model = NutritionDay
    template_name = 'nutrition/day/day-details.html'
    context_object_name = 'day'
    http_method_names = ['get']


    def get_context_data(self,**kwargs):

        context = super().get_context_data(**kwargs)
        day = get_object_or_404(NutritionDay, pk=self.kwargs['pk'])

        if day:
            ordered_meals = list(day.meals.all())

            for meal in ordered_meals:
                meal.totals = NutritionCalculator.calculate_meal_totals(meal)

            day.totals = NutritionCalculator.calculate_day_totals(day)
            day.ordered_meals = ordered_meals

        context['day'] = day

        return context


class DayCreateView(CreateView):
    model = NutritionDay
    fields = ['name']
    template_name = 'nutrition/day/day-create.html'

    def form_valid(self, form):
        messages.success(self.request, 'The day has been created successfully!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('nutrition:day-details', kwargs={'pk': self.object.pk})


class DayDeleteView(DeleteView):
    model = NutritionDay
    template_name = 'nutrition/day/day-delete.html'
    context_object_name = 'day'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'The day has been deleted successfully!')
        return super().delete(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('nutrition:nutrition-home')


class DayEditView(UpdateView):
    model = NutritionDay
    fields = '__all__'
    template_name = 'nutrition/day/day-edit.html'

    def form_valid(self, form):
        messages.success(self.request, 'The day has been updated successfully!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('nutrition:day-details', kwargs={'pk': self.object.pk})



class FoodDatabaseListView(ListView):
    model = FoodDatabase
    template_name = 'nutrition/food-database/food-database-list.html'
    context_object_name = 'foods'
    paginate_by = 10


class FoodDatabaseCreateView(CreateView):
    model = FoodDatabase
    fields = '__all__'
    template_name = 'nutrition/food-database/food-database-create.html'

    def form_valid(self, form):
        messages.success(self.request, 'The item has been created successfully!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('nutrition:food-database-list')


class FoodDatabaseDeleteView(DeleteView):
    model = FoodDatabase
    template_name = 'nutrition/food-database/food-database-delete.html'
    context_object_name = 'food'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'The item has been deleted successfully!')
        return super().delete(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('nutrition:food-database-list')


class FoodDatabaseEditView(UpdateView):
    model = FoodDatabase
    fields = '__all__'
    template_name = 'nutrition/food-database/food-database-edit.html'
    context_object_name = 'food'

    def form_valid(self, form):
        messages.success(self.request, 'The item has been updated successfully!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('nutrition:food-database-list')

