from django.core.validators import MinValueValidator
from django.db import models

from choices import WeekDaysChoices
from common.models import BaseModel


# Create your models here.

class MuscleGroup(BaseModel):
    ...


class MuscleType(BaseModel):

    group_of_muscles = models.ForeignKey(
        'MuscleGroup',
        on_delete=models.CASCADE,
        related_name='belongs_muscle_types',
    )


class Exercise(BaseModel):

    sets = models.SmallIntegerField(
        validators=[
            MinValueValidator(1)
        ]
    )
    repetitions = models.SmallIntegerField(
        validators=[
            MinValueValidator(1)
        ]
    )
    video_link = models.URLField()

    type_of_muscle = models.ForeignKey(
        'MuscleType',
        on_delete=models.CASCADE,
        related_name='trained_muscle'
    )

    muscles_group = models.ForeignKey(
        'MuscleGroup',
        on_delete=models.SET_NULL,
        related_name='trained_muscle_group',
        null=True,
        blank=True,
    )

    secondary_muscles = models.ManyToManyField(
        'MuscleType',
        related_name='trained_other_muscles',
        blank=True,
    )
    split = models.ForeignKey(
        'TrainingDay',
        on_delete=models.CASCADE,
        related_name='exercise_split',
        null=True,
        blank=True,
    )



class TrainingDay(models.Model):
    day = models.CharField(
        max_length=15,
        choices=WeekDaysChoices.choices,
    )
    description = models.CharField(
        max_length=100,
    )
    muscle_group = models.ManyToManyField(
        'MuscleGroup',
        related_name='training_muscle_group',
    )
    training_muscles = models.ManyToManyField(
        'MuscleType',
        related_name='muscles_trained',
    )
    exercises = models.ManyToManyField(
        'Exercise',
        related_name= 'training_exercise'
    )


    def __str__(self):
        return f"{self.day} - {self.description}"







