from decimal import Decimal

from nutrition.models import Meal


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