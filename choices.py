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
    PRE_WORKOUT = "Pre Workout", "Pre Workout"
    POST_WORKOUT = "Post Workout", "Post Workout"
    DINNER = "Dinner", "Dinner"


class MeasurementsChoices(models.TextChoices):
    GRAM = "Gr.", "Grams"
    PIECE = "Pcs.", "Pieces"
    ML = "Ml.", "Milliliters"


class GenderChoices(models.TextChoices):
    MALE = "Male", "Male"
    FEMALE = "Female", "Female"


class FitnessGoalChoices(models.TextChoices):
    LOSE_FAT = "Lose fat", "Lose fat"
    BUILD_MUSCLE = "Build muscle", "Build muscle"
    MAINTAIN = "Maintain", "Maintain"


class ActivityLevelChoices(models.TextChoices):
    SEDENTARY = "Sedentary", "Sedentary"
    LIGHT = "Lightly", "Lightly active"
    MODERATE = "Moderate", "Moderately active"
    ACTIVE = "Active", "Active"
    VERY_ACTIVE = "Very", "Very active"


class ExperienceLevelChoices(models.TextChoices):
    BEGINNER = "Beginner", "Beginner"
    INTERMEDIATE = "Intermediate", "Intermediate"
    ADVANCED = "Advanced", "Advanced"

