from django.core.validators import MinValueValidator
from django.db import models

from choices import MealTypeChoices, WeekDaysChoices, MeasurementsChoices
from common.models import BaseModel


class FoodDatabase(BaseModel):

    calories = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[
            MinValueValidator(0)
        ]
    )

    protein = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[
            MinValueValidator(0)
        ]
    )

    carbohydrates = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[
            MinValueValidator(0)
        ]
    )

    fat = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[
            MinValueValidator(0)
        ]
    )


class Meal(models.Model):

    name = models.CharField(
        max_length=50,
        choices=MealTypeChoices.choices,
    )
    day = models.CharField(
        max_length=50,
        choices=WeekDaysChoices.choices,
    )
    time = models.TimeField()

    def __str__(self):
        return f"{self.day} - {self.name}"



class MealFoodItem(models.Model):
    meal = models.ForeignKey(
        'Meal',
        on_delete=models.CASCADE,
    )
    food = models.ForeignKey(
        'FoodDatabase',
        on_delete=models.CASCADE,
    )
    measure = models.CharField(
        max_length=50,
        choices=MeasurementsChoices.choices,
    )
    quantity = models.DecimalField(
        max_digits=6,
        decimal_places=2
    )


class NutritionDay(models.Model):

    name = models.CharField(
        max_length=50,
        choices=WeekDaysChoices.choices,
    )
    meals = models.ManyToManyField(
        'Meal',
        related_name='nutrition_days',
    )


