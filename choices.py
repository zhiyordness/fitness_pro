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
    BREAKFAST = "BF", "Breakfast"
    SNACK = "SN", "Snack"
    PRE_WORKOUT = "PRE", "Pre workout"
    POST_WORKOUT = "POST", "Post workout"
    DINNER = "DIN", "Dinner"


class MeasurementsChoices(models.TextChoices):
    GRAM = "GR", "Grams"
    PIECE = "P", "Pieces"
    ML = "ML", "Milliliters"
