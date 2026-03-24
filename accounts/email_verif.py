import ssl

import certifi
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.urls import reverse

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

    context = {
        'user': user,
        'verification_link': verification_link,
        'expiration_hours': 24,
        'site_name': 'FitnessPro',
    }
    try:
        html_content = render_to_string('accounts/emails/verify_email.html', context)

        text_content = (f"Hello {user.email},"
                        f"\n\nPlease verify your email by clicking the following link: {verification_link}"
                        f"\n\nThis link will expire in 24 hours."
                        f"\n\nIf you didn't register for Fitness Pro, please ignore this email."
                        f"\n\nBest regards,"
                        f"\nFitness Pro Team")

        msg = EmailMultiAlternatives(
            subject='Verify Your Email for Fitness Pro',
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email],
            reply_to=[settings.DEFAULT_FROM_EMAIL],
        )
        msg.attach_alternative(html_content, "text/html")

        ssl_context = ssl.create_default_context(cafile=certifi.where())
        msg.connection = None

        msg.send(fail_silently=False)
        return True, "Verification email sent successfully."

    except Exception as e:
        print(f"Failed to send verification email: {e}")
        return False, f"Failed to send verification email: {str(e)}"
