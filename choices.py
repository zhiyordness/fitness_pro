from django.db import models


class WeekDaysChoices(models.TextChoices):
    MONDAY = "Mon", "Monday"
    TUESDAY = "Tue", "Tuesday"
    WEDNESDAY = "Wed", "Wednesday"
    THURSDAY = "Thur", "Thursday"
    FRIDAY = "Fri", "Friday"
    SATURDAY = "Sat", "Saturday"
    SUNDAY = "Sun", "Sunday"


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
