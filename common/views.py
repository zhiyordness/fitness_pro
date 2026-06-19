from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.utils.translation import gettext_lazy as _

from choices import FitnessGoalChoices
from nutrition.services import NutritionService
from nutrition.views import NutritionCalculator
from datetime import date, datetime
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.utils import timezone
from django.views import View
from nutrition.models import Meal
from progress.models import ProgresTracking
from training.models import TrainingDay



class HomePageView(LoginRequiredMixin, View):
    template_name = 'home/home-page.html'

    def get_weight_change(self, user):
        weight_records = list(ProgresTracking.objects.filter(owner=user).order_by('-date')[:2])

        if len(weight_records) >= 2:
            current_weight = weight_records[0].weight
            previous_weight = weight_records[1].weight
            return current_weight - previous_weight
        return 0


    def get(self, request, *args, **kwargs):
        today_name = date.today().strftime('%A')

        training_day = TrainingDay.objects.filter(
            owner=request.user,
            day__iexact=today_name,
        ).first()

        next_meal = NutritionService.get_next_planned_meal(
            request.user,
            today_name,
        )

        if next_meal:
            total_calories = NutritionCalculator.calculate_meal_totals(next_meal)['calories']
        else:
            total_calories = 0

        meal_status = None

        if next_meal:
            meal_status = NutritionService.get_meal_status(
                meal = next_meal,
                user = request.user,
            )

        completed_nutrition = NutritionService.get_today_completed_nutrition_totals(
            request.user
        )

        nutrition_target = getattr(
            request.user,
            'nutrition_target',
            None,
        )

        nutrition_progress = {
            'calories': 0,
            'protein': 0,
            'carbohydrates': 0,
            'fat': 0,
        }

        if nutrition_target:

            if nutrition_target.calories:
                nutrition_progress['calories'] = round(
                    min(
                        100,
                        (completed_nutrition['calories'] / nutrition_target.calories) * 100
                    ),
                    1
                )

            if nutrition_target.protein:
                nutrition_progress['protein'] = round(
                    min(
                        100,
                        (completed_nutrition['protein'] / nutrition_target.protein) * 100
                    ),
                    1
                )

            if nutrition_target.carbohydrates:
                nutrition_progress['carbohydrates'] = round(
                    min(
                        100,
                        (completed_nutrition['carbohydrates'] / nutrition_target.carbohydrates) * 100
                    ),
                    1
                )

            if nutrition_target.fat:
                nutrition_progress['fat'] = round(
                    min(
                        100,
                        (completed_nutrition['fat'] / nutrition_target.fat) * 100
                    ),
                    1
                )

        weekly_nutrition = NutritionService.get_weekly_nutrition_totals(
            request.user
        )

        weekly_progress = {
            'calories': 0,
            'protein': 0,
            'carbohydrates': 0,
            'fat': 0,
        }

        if nutrition_target:

            weekly_calories_target = nutrition_target.calories * 7
            weekly_protein_target = nutrition_target.protein * 7
            weekly_carbohydrates_target = nutrition_target.carbohydrates * 7
            weekly_fat_target = nutrition_target.fat * 7

            if weekly_calories_target:
                weekly_progress['calories'] = round(
                    min(
                        100,
                        (weekly_nutrition['calories'] / weekly_calories_target) * 100
                    ),
                    1
                )

            if weekly_protein_target:
                weekly_progress['protein'] = round(
                    min(
                        100,
                        (weekly_nutrition['protein'] / weekly_protein_target) * 100
                    ),
                    1
                )

            if weekly_carbohydrates_target:
                weekly_progress['carbohydrates'] = round(
                    min(
                        100,
                        (weekly_nutrition['carbohydrates'] / weekly_carbohydrates_target) * 100
                    ),
                    1
                )

            if weekly_fat_target:
                weekly_progress['fat'] = round(
                    min(
                        100,
                        (weekly_nutrition['fat'] / weekly_fat_target) * 100
                    ),
                    1
                )
        weekly_targets = {
            'calories': nutrition_target.calories * 7 if nutrition_target else 0,
            'protein': nutrition_target.protein * 7 if nutrition_target else 0,
            'carbohydrates': nutrition_target.carbohydrates * 7 if nutrition_target else 0,
            'fat': nutrition_target.fat * 7 if nutrition_target else 0,
        }

        meal_consistency = NutritionService.get_meal_consistency(
            request.user
        )

        daily_nutrition_progress = NutritionService.get_nutrition_progress(request.user)

        weight_change = self.get_weight_change(request.user)
        current_weight_record = ProgresTracking.objects.filter(owner=request.user).order_by('-date').first()

        profile = getattr(request.user, 'profile', None)

        target_weight = profile.target_weight if profile else None

        remaining_weight = None

        if profile and current_weight_record and target_weight:

            current_weight = current_weight_record.weight

            if profile.fitness_goal == FitnessGoalChoices.LOSE_FAT:
                remaining_weight = current_weight - target_weight

            elif profile.fitness_goal == FitnessGoalChoices.BUILD_MUSCLE:
                remaining_weight = target_weight - current_weight

        goal_progress = None
        if (
            profile and profile.starting_weight and target_weight and current_weight_record
        ):

            start_weight = profile.starting_weight
            current_weight = current_weight_record.weight

            if profile.fitness_goal == FitnessGoalChoices.LOSE_FAT:
                total = start_weight - target_weight
                completed = start_weight - current_weight

            elif profile.fitness_goal == FitnessGoalChoices.BUILD_MUSCLE:
                total = target_weight - start_weight
                completed = current_weight - start_weight

            else: #Maintanin
                total = 0
                completed = 0

            if total > 0:
                goal_progress = round(
                    max(0, min(100, (completed / total) * 100)), 1
                )
        # print(
        #     f"Start: {profile.starting_weight}, "
        #     f"Current: {current_weight_record.weight}, "
        #     f"Target: {target_weight}, "
        #     f"Goal: {profile.fitness_goal}, "
        #     f"Progress: {goal_progress}"
        # )

        dashboard =  {
            'current_weight': current_weight_record.weight if current_weight_record else None,
            'target_weight': target_weight,
            'remaining_weight': remaining_weight,
            'weight_change': weight_change,

            'goal_progress': goal_progress,

            'completed_nutrition': completed_nutrition,
            'nutrition_target': nutrition_target,
            'nutrition_progress': nutrition_progress,
            'weekly_nutrition': weekly_nutrition,
            'weekly_progress': weekly_progress,
            'weekly_targets': weekly_targets,

            'daily_nutrition_progress': daily_nutrition_progress,

            'meal_consistency': meal_consistency,

            'training_day': training_day,

            'meal_status': meal_status,

            'next_meal': next_meal,
            'total_calories': total_calories,
        }

        context = {
            'dashboard': dashboard,
        }

        # print(f"Meal Status: {meal_status}")
        # print(completed_nutrition)
        # print(nutrition_progress)
        # print(weekly_nutrition)
        # print(weekly_progress)
        print(meal_consistency)

        return render(request, self.template_name, context)



def page_not_found_view(request: HttpRequest, exception) -> HttpResponse:
    return render(request, 'errors/404.html', status=404)


