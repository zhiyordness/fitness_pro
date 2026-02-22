from django.db import models


class WeekDaysChoices(models.TextChoices):
    MONDAY = "Monday", "Monday"
    TUESDAY = "Tuesday", "Tuesday"
    WEDNESDAY = "Wednesday", "Wednesday"
    THURSDAY = "Thursday", "Thursday"
    FRIDAY = "Friday", "Friday"
    SATURDAY = "Saturday", "Saturday"
    SUNDAY = "Sunday", "Sunday"


class MealTypeChoices(models.TextChoices):
    BREAKFAST = "Breakfast", "Breakfast"
    SNACK = "Snack", "Snack"
    PRE_WORKOUT = "Pre workout", "Pre workout"
    POST_WORKOUT = "Post workout", "Post workout"
    DINNER = "Dinner", "Dinner"


class MeasurementsChoices(models.TextChoices):
    GRAM = "Gr.", "Grams"
    PIECE = "Pcs.", "Pieces"
    ML = "Ml.", "Milliliters"
