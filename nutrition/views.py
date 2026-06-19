from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import When, Case, IntegerField
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import DetailView, CreateView, UpdateView, DeleteView, ListView
from choices import WeekDaysChoices, MealStatusChoices
from common.mixins import StaffRequiredMixin
from nutrition.forms import MealForm, MealFoodItemForm, DayCreateForm, NutritionTargetForm
from nutrition.models import Meal, MealFoodItem, NutritionDay, FoodDatabase, MealCompletion, NutritionTarget
from nutrition.services import NutritionCalculator, NutritionService
from django.utils.translation import gettext_lazy as _
from datetime import datetime


class NutritionHomeView(LoginRequiredMixin, ListView):
    model = NutritionDay
    template_name = 'nutrition/nutrition-overview.html'
    context_object_name = 'days'

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
        return NutritionDay.objects.filter(
            owner=self.request.user
        ).annotate(
            days_order=Case(*order_days, output_field=IntegerField())
        ).order_by('days_order').prefetch_related(
            'meals',
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
                meal.status = NutritionService.get_meal_status(
                    meal,
                    self.request.user,
                )

            day_totals[day.pk] = NutritionCalculator.calculate_day_totals(day)
            day.ordered_meals = ordered_meals

        today_name = timezone.now().strftime('%A')

        context['day_totals'] = day_totals
        context['today_name'] = today_name

        return context


class MealDetailsView(LoginRequiredMixin, DetailView):
    model = Meal
    form_class = MealForm
    template_name = 'nutrition/meal/meal-details.html'
    context_object_name = 'meal'
    http_method_names = ['get']

    def get_queryset(self):
        return Meal.objects.filter(day__owner=self.request.user).prefetch_related(
            'mealfooditem_set__food',
        )



class MealCreateView(LoginRequiredMixin, CreateView):
    model = Meal
    form_class = MealForm
    template_name = 'nutrition/meal/meal-create.html'

    def form_valid(self, form):
        day = get_object_or_404(NutritionDay, pk=self.kwargs['day_pk'])
        meal_name = form.cleaned_data['name']
        form.instance.order = Meal.get_order_for_name(meal_name)
        form.instance.day = day
        messages.success(self.request, _('The Meal has been created successfully!'))
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('nutrition:day-details', kwargs={'pk': self.object.day.pk})


class MealEditView(LoginRequiredMixin, UpdateView):
    model = Meal
    form_class = MealForm
    template_name = 'nutrition/meal/meal-edit.html'

    def form_valid(self, form):
        meal_name = form.cleaned_data['name']
        form.instance.order = Meal.get_order_for_name(meal_name)

        messages.success(self.request, _('The meal has been updated successfully!'))
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('nutrition:day-details',kwargs={'pk': self.object.day.pk})

    def get_queryset(self):
        return Meal.objects.filter(day__owner=self.request.user)



class MealDeleteView(LoginRequiredMixin, DeleteView):
    model = Meal
    template_name = 'nutrition/meal/meal-delete.html'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, _('The meal has been deleted successfully!'))
        return super().delete(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('nutrition:day-details',kwargs={'pk': self.object.day.pk})

    def get_queryset(self):
        return Meal.objects.filter(day__owner=self.request.user)



class ItemAddView(LoginRequiredMixin, CreateView):
    model = MealFoodItem
    form_class = MealFoodItemForm
    template_name = 'nutrition/item/item-add.html'

    def dispatch(self, request, *args, **kwargs):
        self.meal = get_object_or_404(Meal, pk=self.kwargs['pk'], day__owner=self.request.user)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.meal = self.meal
        messages.success(self.request, _('The item has been created successfully!'))
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('nutrition:day-details', kwargs={'pk': self.meal.day.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['meal'] = self.meal
        return context


class ItemEditView(LoginRequiredMixin, UpdateView):
    model = MealFoodItem
    form_class = MealFoodItemForm
    template_name = 'nutrition/item/item-edit.html'

    def get_queryset(self):
        return MealFoodItem.objects.filter(
            meal__day__owner=self.request.user,
        )

    def form_valid(self, form):
        messages.success(
            self.request,
            _('The item has been updated successfully!')
        )

        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            'nutrition:day-details',
            kwargs={
                'pk': self.object.meal.day.pk,
            }
        )

class ItemDeleteView(LoginRequiredMixin, DeleteView):
    model = MealFoodItem
    template_name = 'nutrition/item/item-delete.html'
    context_object_name = 'item'

    def get_success_url(self):
        return reverse_lazy(
            'nutrition:day-details',
            kwargs={'pk': self.object.meal.day.pk}
        )

    def get_queryset(self):
        return MealFoodItem.objects.filter(meal__day__owner=self.request.user)



class DayDetailsView(LoginRequiredMixin, DetailView):
    model = NutritionDay
    template_name = 'nutrition/day/day-details.html'
    context_object_name = 'day'

    def get_queryset(self):
        return NutritionDay.objects.filter(
            owner=self.request.user
        ).prefetch_related(
            'meals__mealfooditem_set__food',
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        day = self.object

        ordered_meals = day.meals.all().order_by('order')

        for meal in ordered_meals:
            meal.totals = NutritionCalculator.calculate_meal_totals(meal)

            items = list(meal.mealfooditem_set.all())

            for item in items:
                totals = NutritionCalculator.calculate_item_totals(item)

                item.total_calories = totals['calories']
                item.total_protein = totals['protein']
                item.total_carbohydrates = totals['carbohydrates']
                item.total_fat = totals['fat']

            meal.items = items

        day.totals = NutritionCalculator.calculate_day_totals(day)
        day.ordered_meals = ordered_meals

        context['day'] = day

        return context


class DayCreateView(LoginRequiredMixin, CreateView):
    model = NutritionDay
    form_class = DayCreateForm
    template_name = 'nutrition/day/day-create.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.owner = self.request.user
        messages.success(self.request, _('The day has been created successfully!'))
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('nutrition:day-details', kwargs={'pk': self.object.pk})

class DayDeleteView(LoginRequiredMixin, DeleteView):
    model = NutritionDay
    template_name = 'nutrition/day/day-delete.html'
    context_object_name = 'day'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, _('The day has been deleted successfully!'))
        return super().delete(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('nutrition:nutrition-home')

    def get_queryset(self):
        return NutritionDay.objects.filter(owner=self.request.user)



class DayEditView(LoginRequiredMixin, UpdateView):
    model = NutritionDay
    fields = ['name']
    template_name = 'nutrition/day/day-edit.html'

    def form_valid(self, form):
        messages.success(self.request, _('The day has been updated successfully!'))
        return super().form_valid(form)

    def get_queryset(self):
        return NutritionDay.objects.filter(owner=self.request.user)

    def get_success_url(self):
        return reverse_lazy('nutrition:day-details', kwargs={'pk': self.object.pk})



class FoodDatabaseListView(ListView):
    model = FoodDatabase
    template_name = 'nutrition/food-database/food-database-list.html'
    context_object_name = 'foods'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(name__icontains=search_query)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        context['total_foods'] = FoodDatabase.objects.count()
        return context


class FoodDatabaseCreateView(StaffRequiredMixin, CreateView):
    model = FoodDatabase
    fields = '__all__'
    template_name = 'nutrition/food-database/food-database-create.html'

    def form_valid(self, form):
        messages.success(self.request, _('The item has been created successfully!'))
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('nutrition:food-database-list')


class FoodDatabaseDeleteView(StaffRequiredMixin, DeleteView):
    model = FoodDatabase
    template_name = 'nutrition/food-database/food-database-delete.html'
    context_object_name = 'food'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, _('The item has been deleted successfully!'))
        return super().delete(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('nutrition:food-database-list')


class FoodDatabaseEditView(StaffRequiredMixin, UpdateView):
    model = FoodDatabase
    fields = '__all__'
    template_name = 'nutrition/food-database/food-database-edit.html'
    context_object_name = 'food'

    def form_valid(self, form):
        messages.success(self.request, _('The item has been updated successfully!'))
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('nutrition:food-database-list')


class MealCompleteView(LoginRequiredMixin, View):

    def post(self, request, meal_pk):

        meal = get_object_or_404(
            Meal.objects.filter(
                day__owner=request.user,
            ),
            pk=meal_pk,
        )

        NutritionService.complete_meal(
            meal=meal,
            user=request.user,
        )

        messages.success(
            request,
            _('Meal marked as completed!')
        )

        return redirect('common:home')


class MealMissedView(LoginRequiredMixin, View):

    def post(self, request, meal_pk):

        meal = get_object_or_404(
            Meal.objects.filter(
                day__owner=request.user,
            ),
            pk=meal_pk,
        )

        NutritionService.miss_meal(
            meal=meal,
            user=request.user,
        )

        messages.success(
            request,
            _('Meal marked as missed!')
        )

        return redirect('common:home')


class MealPlannedView(LoginRequiredMixin, View):

    def post(self, request, meal_pk):

        meal = get_object_or_404(
            Meal,
            pk=meal_pk,
        )

        completion = MealCompletion.objects.filter(
            meal=meal,
            user=request.user,
        ).first()

        if completion:
            completion.status = MealStatusChoices.PLANNED
            completion.save()

        messages.success(
            request,
            _('Meal reset to planned!')
        )

        return redirect('nutrition:nutrition-home')


class NutritionTargetUpdateView(LoginRequiredMixin, UpdateView,):
    model = NutritionTarget
    form_class = NutritionTargetForm
    template_name = 'nutrition/target-edit.html'

    def get_object(self, queryset=None):
        nutrition_target, _ = NutritionTarget.objects.get_or_create(
            user=self.request.user,
            defaults={
                'calories': 2000,
                'protein': 150,
                'carbohydrates': 250,
                'fat': 60,
            }
        )

        return nutrition_target

    def get_success_url(self):
        return reverse_lazy(
            'nutrition:nutrition-target-edit'
        )

    def form_valid(self, form):
        messages.success(
            self.request,
            _('Nutrition goals updated successfully!')
        )

        return super().form_valid(form)