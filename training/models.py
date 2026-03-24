from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse

from choices import WeekDaysChoices
from common.models import BaseModel


UserModel = get_user_model()

class Exercise(BaseModel):
    muscles = models.ManyToManyField(
        'Muscle',
        related_name='exercises',
    )

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

    class Meta:
        indexes = [
            models.Index(fields=['name']),
        ]


class MuscleGroup(BaseModel):
    ...


class Muscle(BaseModel):

    group = models.ForeignKey(
        'MuscleGroup',
        on_delete=models.CASCADE,
        related_name='muscles',
    )




class TrainingDay(models.Model):

    owner = models.ForeignKey(
        UserModel,
        on_delete=models.CASCADE,
        related_name='training_days',
    )

    day = models.CharField(
        max_length=15,
        choices=WeekDaysChoices.choices,
    )

    description = models.CharField(
        max_length=300,
    )
    muscle_groups = models.ManyToManyField(
        'MuscleGroup',
        related_name='training_days',
    )
    exercises = models.ManyToManyField(
        'Exercise',
        related_name= 'training_days',
        blank=True
    )

    def get_absolute_url(self):
        return reverse('training:details', kwargs={'pk': self.pk})

    def __str__(self):
        return f"{self.get_day_display()} - {self.owner.username} - {self.description}"

    class Meta:
        ordering = ['owner', 'day']
        unique_together = ['owner', 'day']
        indexes = [
            models.Index(fields=['owner', 'day']),
            models.Index(fields=['owner']),
        ]

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


