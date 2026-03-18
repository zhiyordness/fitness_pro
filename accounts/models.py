import secrets
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models

from accounts.managers import FitnessProUserManager
from choices import GenderChoices, FitnessGoalChoices, ActivityLevelChoices, ExperienceLevelChoices
from common.validators import ImageValidator


# Create your models here.

class FitnessProUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(
        null=False,
        blank=False,
        unique=True
    )
    is_active = models.BooleanField(
        default=False,
    )
    is_staff = models.BooleanField(
        default=False,
    )
    registration_date = models.DateTimeField(
        auto_now_add=True,
    )
    is_email_verified = models.BooleanField(
        default=False,
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = FitnessProUserManager()

    def __str__(self):
        return self.email


class Profile(models.Model):
    user = models.OneToOneField(
        'FitnessProUser',
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='profile'
    )
    first_name = models.CharField(
        max_length=50,
        null=True,
        blank=True,
    )
    last_name = models.CharField(
        max_length=50,
        null=True,
        blank=True,
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
        max_length=500,
        validators=[
            ImageValidator(),
        ],
        help_text='Upload a profile picture (max size: 5MB, min: 200x200px, formats: JPEG, PNG).'
    )

    def __str__(self):
        return self.get_full_name()

    def get_full_name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.user.email



class EmailVerificationToken(models.Model):
    user = models.OneToOneField(
        'FitnessProUser',
        on_delete=models.CASCADE,
        related_name='email_verification_token'
    )
    token = models.CharField(
        max_length=100,
        unique=True,
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    class Meta:
        indexes = [
            models.Index(fields=['token']),
            models.Index(fields=['expires_at']),
        ]

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = secrets.token_urlsafe(48)

        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(hours=24)

        super().save(*args, **kwargs)

    def is_valid(self):
        return timezone.now() <= self.expires_at

    def __str__(self):
        return f"Verification token for {self.user.email}"
