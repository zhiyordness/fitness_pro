from django.contrib import messages
from django.contrib.auth import get_user_model, logout, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView

from django.shortcuts import redirect, get_object_or_404, render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.cache import never_cache
from django.views.generic import CreateView, DetailView, UpdateView, DeleteView, RedirectView
from django.utils.translation import gettext_lazy as _
from accounts.email_verif import send_verification_email
from accounts.forms import FitnessProUserCreationForm, ProfileForm, UserDeleteForm
from accounts.models import Profile, EmailVerificationToken, FitnessProUser
import logging

from nutrition.services import NutritionService

logger = logging.getLogger(__name__)

# Create your views here.

UserModel = get_user_model()


class FitnessProUserRegisterView(CreateView):
    model = UserModel
    form_class = FitnessProUserCreationForm
    template_name = 'accounts/register-page.html'
    success_url = reverse_lazy('accounts:login')

    def form_valid(self, form):
        response = super().form_valid(form)

        logger.info(
            'User registered successfully.',
            extra={
                'user_id': self.object.pk,
                'email': self.object.email,
            },
        )

        success, message = send_verification_email(self.request, self.object)
        if success:
            logger.info(
                'Verification email sent successfully.',
                extra={
                    'user_id': self.object.pk,
                    'email': self.object.email,
                },
            )
            messages.success(self.request, _('Your account has been created successfully! Please check your email to verify your account.'))
        else:
            self.object.delete()
            logger.error(
                'Failed to send verification email. Registration rolled back.',
                extra={
                    'user_id': self.object.pk,
                    'email': self.object.email,
                },
            )
            messages.error(self.request, _('Registration failed due to email delivery issue. Please try again.'))
            return self.form_invalid(form)
        return redirect('accounts:login')

    def form_invalid(self, form):
        logger.warning(
            'User registration validation failed.',
            extra={
                'errors': form.errors.as_json()
            },
        )
        messages.error(self.request, _('There was an error with your registration. Please correct the errors below and try again.'))
        return super().form_invalid(form)


class ProfileDetailView(LoginRequiredMixin, DetailView):
    model = Profile
    form_class = ProfileForm
    template_name = 'accounts/profile-details.html'
    context_object_name = 'profile'

    def get_object(self, queryset = None):
        return self.request.user.profile

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['nutrition_target'] = getattr(
            self.request.user,
            'nutrition_target',
            None,
        )

        return context

    def get_success_url(self):
        return reverse_lazy('accounts:profile-details', kwargs={'pk': self.object.pk})


class ProfileEditView(LoginRequiredMixin, UpdateView):
    model = Profile
    form_class = ProfileForm
    template_name = 'accounts/profile-edit-page.html'

    def get_success_url(self):
        return reverse_lazy('accounts:profile-details', kwargs={'pk': self.object.pk})

    def get_object(self, queryset = None):
        return self.request.user.profile

    def form_valid(self, form):
        messages.success(self.request, _('Your profile has been updated successfully!'))

        logger.info(
            'User profile updated successfully.',
            extra={
                'user_id': self.object.user.pk,
                'email': self.object.user.email,
            }
        )

        return super().form_valid(form)


class DeleteUserView(LoginRequiredMixin, DeleteView):
    model = UserModel
    template_name = 'accounts/profile-delete-page.html'
    form_class = UserDeleteForm

    def get_object(self, queryset=None):
        return self.request.user

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return self.delete(request, *args, **kwargs)
        else:
            return self.form_invalid(form)

    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)

        logger.info(
            'User account deleted successfully.',
            extra={
                'user_id': self.object.pk,
                'email': self.object.email,
            },
        )

        logout(request)
        messages.success(self.request, _('Your profile has been deleted successfully!'))
        return response

    def get_success_url(self):
        return reverse_lazy('common:home')


class InitialLoginView(LoginView):
    template_name = 'accounts/login-page.html'

    def form_valid(self, form):
        user = form.get_user()

        logger.info(
            'User logged in successfully.',
            extra={
                'user_id': user.pk,
                'email': user.email,
            }
        )

        is_first_login = user.last_login is None

        self.request.session['is_first_login'] = is_first_login

        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('accounts:login-redirect')


class LoginRedirectView(LoginRequiredMixin, RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        is_first_login = self.request.session.pop('is_first_login', False)

        if is_first_login:
            return reverse_lazy('accounts:profile-edit', kwargs={'pk': self.request.user.profile.pk})
        else:
            return reverse_lazy('common:home')

@method_decorator(never_cache, name='dispatch')
class VerifyEmailView(View):

    def get(self, request, token):

        token_object = get_object_or_404(EmailVerificationToken, token=token)
        if not token_object.is_valid():

            logger.warning(
                'Attempted to verify email with expired token.',
                extra={
                    'user_id': token_object.user.pk,
                    'email': token_object.user.email,
                },
            )

            messages.error(request, _('This verification link has expired. Please request a new one.'))
            return redirect('accounts:resend-verification')

        user = token_object.user

        if user.is_email_verified:

            logger.info(
                'Attempted to verify email for already verified user.',
                extra={
                    'user_id': user.pk,
                    'email': user.email,
                },
            )

            messages.info(request, _('Your email is already verified. Please log in.'))
            return redirect('accounts:login')

        user.is_email_verified = True
        user.is_active = True
        user.save()

        logger.info(
            'User email verified successfully.',
            extra={
                'user_id': user.pk,
                'email': user.email,
            },
        )

        token_object.delete()

        messages.success(request, _('Your email has been verified successfully! Your account is now active. You can now log in.'))

        return redirect('accounts:login')


class ResendVerificationEmailView(View):

    def get(self, request):
        return render(request, 'accounts/emails/resend_verification.html')

    def post(self, request):
        email = request.POST.get('email', '').strip()


        user = FitnessProUser.objects.filter(email=email, is_email_verified=False).first()
        if user:
            if hasattr(user, 'email_verification_token'):
                token = user.email_verification_token
                if not token.is_valid():
                    token.delete()

            send_verification_email(request, user)

        logger.info(
            'Verification email resent.',
            extra={
                'user_id': user.pk ,
                'email': user.email,
            },
        )

        messages.success(request, _('If an account with that email exists and is not verified, a verification email has been sent.'))

        return redirect('accounts:login')

