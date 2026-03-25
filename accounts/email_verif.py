from django.urls import reverse
from .tasks import send_verification_email_task
from accounts.models import EmailVerificationToken


def create_verification_token(user):
    token, created = EmailVerificationToken.objects.update_or_create(
        user=user,
        defaults={}
    )
    return token

def send_verification_email(request, user):

    token_object = create_verification_token(user)
    verification_link = request.build_absolute_uri(
        reverse('accounts:verify-email', kwargs={'token': token_object.token})
    )

    send_verification_email_task.delay(user.email, verification_link)

    return True, "Verification email queued for sending"