from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from choices import WeekDaysChoices
from common.validators import ImageValidator

UserModel = get_user_model()

class ProgresTracking(models.Model):
    owner = models.ForeignKey(
        UserModel,
        on_delete=models.CASCADE,
        related_name='progress_tracking',
    )
    day = models.CharField(
        max_length=50,
        choices=WeekDaysChoices.choices,
    )

    date = models.DateTimeField(
        auto_now_add=True,
    )
    weight = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(350),
        ]
    )
    chest = models.SmallIntegerField(
        validators=[
            MinValueValidator(0)
        ]
    )
    shoulders = models.SmallIntegerField(
        validators=[
            MinValueValidator(0)
        ]
    )
    waist = models.SmallIntegerField(
        validators=[
            MinValueValidator(0)
        ]
    )
    biceps = models.SmallIntegerField(
        validators=[
            MinValueValidator(0)
        ]
    )
    neck = models.SmallIntegerField(
        validators=[
            MinValueValidator(0)
        ]
    )
    butt = models.SmallIntegerField(
        validators=[
            MinValueValidator(0)
        ]
    )
    tight = models.SmallIntegerField(
        validators=[
            MinValueValidator(0)
        ]
    )
    calf = models.SmallIntegerField(
        validators=[
            MinValueValidator(0)
        ]
    )
    picture = models.ImageField(
        upload_to='progres_images/',
        max_length=500,
        null=True,
        blank=True,
        validators=[
            ImageValidator(),
        ],
        help_text='Upload a progress picture (max size: 5MB, min: 200x200px, formats: JPEG, PNG).'
    )

    def __str__(self):
        return f"Progress for {self.owner.email} on {self.date.strftime('%Y-%m-%d')}"

    class Meta:
        ordering = ['-date']

