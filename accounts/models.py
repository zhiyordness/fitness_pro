from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models

from accounts.managers import FitnessProUserManager
from choices import GenderChoices, FitnessGoalChoices, ActivityLevelChoices, ExperienceLevelChoices


# Create your models here.

class FitnessProUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(
        null=False,
        blank=False,
        unique=True
    )
    first_name = models.CharField(
        max_length=50,
        null=False,
        blank=False
    )
    last_name = models.CharField(
        max_length=50,
        null=False,
        blank=False
    )
    is_active = models.BooleanField(
        default=True,
    )
    is_staff = models.BooleanField(
        default=False,
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = FitnessProUserManager()

    def __str__(self):
        return self.get_full_name()

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"


class Profile(models.Model):
    user = models.OneToOneField(
        'FitnessProUser',
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='profile'
    )
    gender = models.CharField(
        max_length=20,
        choices=GenderChoices.choices,
        null=True,
        blank=True,
    )
    date_of_birth = models.DateField(
        null=True,
        blank=True,
    )
    height = models.IntegerField(
        null=True,
        blank=True,
    )
    target_weight = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
    )
    fitness_goal = models.CharField(
        max_length=20,
        choices=FitnessGoalChoices.choices,
        null=True,
        blank=True,
    )
    activity_level = models.CharField(
        max_length=20,
        choices=ActivityLevelChoices.choices,
        default=ActivityLevelChoices.MODERATE
    )
    experience_level = models.CharField(
        max_length=20,
        choices=ExperienceLevelChoices.choices,
        null=True,
        blank=True,
    )
    bio = models.TextField(
        null=True,
        blank=True,
    )
    profile_picture = models.ImageField(
        upload_to='profile_pictures/',
        null=True,
        blank=True,
    )





