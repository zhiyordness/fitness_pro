from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
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

    def clean(self):
        super().clean()

        if not hasattr(self, 'exercises') or not hasattr(self, 'muscle_groups'):
             return

        muscle_ids = Muscle.objects.filter(
            group__in=self.muscle_groups.all()
        ).values_list('id', flat=True)

        invalid_exercises = []
        for ex in self.exercises.all():
            if not ex.muscles.filter(id__in=muscle_ids).exists():
                invalid_exercises.append(ex.name)

        if invalid_exercises:
            raise ValidationError(
                f"The following exercises are not valid for the selected muscle groups: {', '.join(invalid_exercises)}"
            )

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


