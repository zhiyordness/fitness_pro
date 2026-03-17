from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

from choices import MealTypeChoices, WeekDaysChoices, MeasurementsChoices
from common.models import BaseModel

UserModel = get_user_model()

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

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
        ]


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
        return f"{self.get_name_display()} - {self.day}"

    class Meta:
        ordering = ['order']

    def save(self, *args, **kwargs):

        order_mapping = {
            'Breakfast': 1,
            'Snack': 2,
            'Pre Workout': 3,
            'Post Workout': 4,
            'Dinner': 5,
        }
        self.order = order_mapping.get(self.name, 1)
        super().save(*args, **kwargs)

    @classmethod
    def get_order_for_name(cls, name):

        order_mapping = {
            'Breakfast': 1,
            'Snack': 2,
            'Pre Workout': 3,
            'Post Workout': 4,
            'Dinner': 5,
        }

        return order_mapping.get(name, 1)


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
        decimal_places=2,
        validators=[
            MinValueValidator(1)
        ]
    )
    def __str__(self):
        return f"{self.food.name} - {self.quantity} {self.measure}"



class NutritionDay(models.Model):
    owner = models.ForeignKey(
        UserModel,
        on_delete=models.CASCADE,
        related_name='nutrition_days',
    )
    name = models.CharField(
        max_length=50,
        choices=WeekDaysChoices.choices,
    )

    def __str__(self):
        return self.name

    class Meta:
        unique_together = ('owner', 'name')



