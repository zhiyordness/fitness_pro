from datetime import timedelta
from decimal import Decimal

from django.utils import timezone

from nutrition.models import Meal

from nutrition.models import MealCompletion
from choices import MealStatusChoices


class NutritionCalculator:

    @staticmethod
    def calculate_meal_totals(meal: Meal) -> dict:
        totals = {
            'calories': Decimal('0'),
            'protein': Decimal('0'),
            'carbohydrates': Decimal('0'),
            'fat': Decimal('0'),
        }

        for item in meal.mealfooditem_set.all():

            item_quantity = 0
            if item.measure == 'Gr.':
                item_quantity = item.quantity / Decimal('100')
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


class NutritionService:

    @staticmethod
    def complete_meal(meal, user):

        completion, _ = MealCompletion.objects.get_or_create(
            meal=meal,
            user=user,
        )

        completion.status = MealStatusChoices.COMPLETED
        completion.save()

        return completion

    @staticmethod
    def miss_meal(meal, user):

        completion, _ = MealCompletion.objects.get_or_create(
            meal=meal,
            user=user,
        )

        completion.status = MealStatusChoices.MISSED
        completion.save()

        return completion

    @staticmethod
    def get_meal_status(meal, user):

        completion = MealCompletion.objects.filter(
            meal=meal,
            user=user,
        ).first()

        return completion.status if completion else MealStatusChoices.PLANNED

    @staticmethod
    def get_today_completed_nutrition_totals(user):

        totals = {
            'calories': Decimal('0'),
            'protein': Decimal('0'),
            'carbohydrates': Decimal('0'),
            'fat': Decimal('0'),
        }

        completions = MealCompletion.objects.filter(
            user=user,
            status=MealStatusChoices.COMPLETED,
            completed_at__date=timezone.now().date(),
        ).select_related('meal')

        for completion in completions:

            meal_totals = NutritionCalculator.calculate_meal_totals(
                completion.meal
            )

            for key in totals:
                totals[key] += meal_totals[key]

        return totals

    @staticmethod
    def get_weekly_nutrition_totals(user):

        totals = {
            'calories': Decimal('0'),
            'protein': Decimal('0'),
            'carbohydrates': Decimal('0'),
            'fat': Decimal('0'),
        }

        today = timezone.now().date()
        week_ago = today - timedelta(days=7)

        completed_meals = MealCompletion.objects.filter(
            user=user,
            status=MealStatusChoices.COMPLETED,
            completed_at__date__gte=week_ago,
        )

        for completion in completed_meals:

            meal_totals = NutritionCalculator.calculate_meal_totals(
                completion.meal
            )

            for key in totals:
                totals[key] += meal_totals[key]

        return totals

    from datetime import timedelta
    from django.utils import timezone

    @staticmethod
    def get_meal_consistency(user):

        week_ago = timezone.now() - timedelta(days=7)

        completions = MealCompletion.objects.filter(
            user=user,
            status_updated_at__gte=week_ago,
        )

        completed_count = completions.filter(
            status=MealStatusChoices.COMPLETED,
        ).count()

        missed_count = completions.filter(
            status=MealStatusChoices.MISSED,
        ).count()

        planned_count = completions.filter(
            status=MealStatusChoices.PLANNED,
        ).count()

        total = completed_count + missed_count + planned_count

        if total == 0:
            return {
                'completed_count': 0,
                'missed_count': 0,
                'planned_count': 0,
                'completed': 0,
                'missed': 0,
                'planned': 0,
                'consistency_score': 0,
            }

        return {
            'completed_count': completed_count,
            'missed_count': missed_count,
            'planned_count': planned_count,

            'completed': round(
                (completed_count / total) * 100,
                1,
            ),

            'missed': round(
                (missed_count / total) * 100,
                1,
            ),

            'planned': round(
                (planned_count / total) * 100,
                1,
            ),

            'consistency_score': round(
                (completed_count / total) * 100,
                1,
            ),
        }


    @staticmethod
    def get_next_planned_meal(user, day_name):

        meals = Meal.objects.filter(
            day__owner=user,
            day__name__icontains=day_name,
        ).order_by('time')

        for meal in meals:

            status = NutritionService.get_meal_status(
                meal,
                user,
            )

            if status == MealStatusChoices.PLANNED:
                return meal

        return None