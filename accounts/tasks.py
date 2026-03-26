import ssl
import certifi
from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


@shared_task
def send_verification_email_task(user_email, verification_link):
    try:
        context = {
            'verification_link': verification_link,
            'expiration_hours': 24,
            'site_name': 'FitnessPro',
        }

        class UserPlaceholder:
            def __init__(self, email):
                self.email = email

        context['user'] = UserPlaceholder(user_email)

        html_content = render_to_string('accounts/emails/verify_email.html', context)

        text_content = (f"Hello {user_email},"
                        f"\n\nPlease verify your email by clicking the following link: {verification_link}"
                        f"\n\nThis link will expire in 24 hours."
                        f"\n\nIf you didn't register for Fitness Pro, please ignore this email."
                        f"\n\nBest regards,"
                        f"\nFitness Pro Team")

        msg = EmailMultiAlternatives(
            subject='Verify Your Email for Fitness Pro',
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user_email],
            reply_to=[settings.DEFAULT_FROM_EMAIL],
        )
        msg.attach_alternative(html_content, "text/html")

        ssl_context = ssl.create_default_context(cafile=certifi.where())
        msg.connection = None

        msg.send(fail_silently=False)

        return f"Verification email sent to {user_email}"

    except Exception as e:
        print(f"Failed to send verification email to {user_email}: {e}")
        raise e


@shared_task
def send_password_reset_email_task(user_email, reset_link, user_first_name=None):
    try:
        context = {
            'reset_link': reset_link,
            'expiration_hours': 24,
            'site_name': 'FitnessPro',
            'user_email': user_email,
            'user_first_name': user_first_name or 'User',
        }

        class UserPlaceholder:
            def __init__(self, email, first_name=None):
                self.email = email
                self.first_name = first_name
                self.get_full_name = lambda: first_name or email

        context['user'] = UserPlaceholder(user_email, user_first_name)

        html_content = render_to_string('accounts/password_reset_email.html', context)

        text_content = (f"Hello {user_first_name or user_email},"
                        f"\n\nYou're receiving this email because you requested a password reset for your Fitness Pro account."
                        f"\n\nClick the link below to reset your password:"
                        f"\n{reset_link}"
                        f"\n\nThis link will expire in 24 hours."
                        f"\n\nIf you didn't request a password reset, please ignore this email."
                        f"\n\nBest regards,"
                        f"\nFitness Pro Team")

        msg = EmailMultiAlternatives(
            subject='Reset Your Password - Fitness Pro',
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user_email],
            reply_to=[settings.DEFAULT_FROM_EMAIL],
        )
        msg.attach_alternative(html_content, "text/html")

        ssl_context = ssl.create_default_context(cafile=certifi.where())
        msg.connection = None

        msg.send(fail_silently=False)

        return f"Password reset email sent to {user_email}"

    except Exception as e:
        print(f"Failed to send password reset email to {user_email}: {e}")
        raise e

