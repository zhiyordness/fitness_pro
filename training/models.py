from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.urls import reverse

from choices import WeekDaysChoices, WorkoutSessionStatus
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

    def get_absolute_url(self):
        return reverse('training:details', kwargs={'pk': self.pk})

    def __str__(self):
        return f"{self.get_day_display()} - {self.owner.email} - {self.description}"

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


class TrainingDayExercise(models.Model):

    training_day = models.ForeignKey(
        TrainingDay,
        on_delete=models.CASCADE,
        related_name='training_day_exercises',
    )

    exercise = models.ForeignKey(
        Exercise,
        on_delete=models.CASCADE,
        related_name='training_day_exercises',
    )

    custom_sets = models.PositiveSmallIntegerField()

    custom_repetitions = models.PositiveSmallIntegerField()

    order = models.PositiveSmallIntegerField(
        default=1,
    )

    class Meta:
        ordering = ['order']

        unique_together = (
            'training_day',
            'exercise',
        )


class WorkoutSession(BaseModel):

    owner = models.ForeignKey(
        UserModel,
        on_delete=models.CASCADE,
        related_name='workout_sessions',
    )

    training_day = models.ForeignKey(
        TrainingDay,
        on_delete=models.CASCADE,
        related_name='workout_sessions',
    )

    started_at = models.DateTimeField(
        auto_now_add=True,
    )

    finished_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    status = models.CharField(
        max_length=20,
        choices=WorkoutSessionStatus.choices,
        default=WorkoutSessionStatus.STARTED,
    )

    def __str__(self):
        return f"Workout Session - {self.owner.email} - {self.training_day.day} - {self.started_at}"


class WorkoutExerciseSession(BaseModel):

    workout_session = models.ForeignKey(
        WorkoutSession,
        on_delete=models.CASCADE,
        related_name='exercise_sessions',
    )

    training_day_exercise = models.ForeignKey(
        TrainingDayExercise,
        on_delete=models.CASCADE,
        related_name='exercise_sessions',
    )

    order = models.PositiveSmallIntegerField()


class WorkoutSet(BaseModel):

    exercise_session = models.ForeignKey(
        WorkoutExerciseSession,
        on_delete=models.CASCADE,
        related_name='sets',
    )

    set_number = models.PositiveSmallIntegerField()

    weight = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(500),
        ]
    )

    repetitions = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(50),
        ]
    )

    is_completed = models.BooleanField(
        default=False,
    )

    class Meta:
        ordering = [
            'set_number'
        ]


class PersonalRecord(BaseModel):

    owner = models.ForeignKey(
        UserModel,
        on_delete=models.CASCADE,
        related_name='personal_records',
    )

    exercise = models.ForeignKey(
        Exercise,
        on_delete=models.CASCADE,
        related_name='personal_records',
    )

    workout_set = models.ForeignKey(
        WorkoutSet,
        on_delete=models.CASCADE,
        related_name='personal_records',
    )

    weight = models.DecimalField(
        max_digits=6,
        decimal_places=2,
    )

    repetitions = models.PositiveSmallIntegerField()

    achieved_at = models.DateTimeField()

    class Meta:
        unique_together = (
            'owner',
            'exercise',
        )

        indexes = [
            models.Index(
                fields=[
                    'owner',
                    'exercise',
                ]
            )
        ]

