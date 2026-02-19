from django.core.validators import MinValueValidator
from django.db import models

from choices import MealTypeChoices, WeekDaysChoices, MeasurementsChoices
from common.models import BaseModel


class FoodDatabase(BaseModel):

    calories = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=0,
        validators=[
            MinValueValidator(0)
        ]
    )

    protein = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=0,
        validators=[
            MinValueValidator(0)
        ]
    )

    carbohydrates = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=0,
        validators=[
            MinValueValidator(0)
        ]
    )

    fat = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=0,
        validators=[
            MinValueValidator(0),
        ]
    )


class Meal(models.Model):
    ORDER_CHOICES = [
        (1, 'Breakfast'),
        (2, 'Snack'),
        (3, 'Pre Workout'),
        (4, 'Post Workout'),
        (5, 'Dinner'),
    ]

    day = models.ForeignKey(
        'NutritionDay',
        related_name='meals',
        on_delete=models.CASCADE
    )

    order = models.PositiveSmallIntegerField(
        choices=ORDER_CHOICES,
    )
    name = models.CharField(
        max_length=50,
        choices=MealTypeChoices.choices
    )
    time = models.TimeField()

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['order']






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
        unique=True,
    )

    def __str__(self):
        return self.name


