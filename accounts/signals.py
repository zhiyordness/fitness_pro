import logging

from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed

from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from accounts.models import Profile

logger = logging.getLogger(__name__)

UserModel = get_user_model()

@receiver(post_save, sender=UserModel)
def create_profile(sender, instance, created, **kwargs):
    """
    Ensures that every newly created user has an associated profile.
    Acts as a safety net in case profile creation is skipped elsewhere.
    """
    if created:
        Profile.objects.get_or_create(user=instance)


@receiver(post_save, sender=UserModel)
def save_profile(sender, instance, **kwargs):

    if hasattr(instance, 'profile'):
        instance.profile.save()


@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    logger.info(
        'User logged in successfully.',
        extra={
            'user_id': user.pk,
            'email': user.email,
        },
    )

@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    if user is not None:
        logger.info(
            'User logged out successfully.',
            extra={
                'user_id': user.pk,
                'email': user.email,
            },
        )

@receiver(user_login_failed)
def log_user_login_failed(sender, credentials, request, **kwargs):
    logger.warning(
        'User login failed.',
        extra={
            'login_identifier': credentials.get('username'),
            'ip_address': request.META.get('REMOTE_ADDR') if request else None,
        },
    )
