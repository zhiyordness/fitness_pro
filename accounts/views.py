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

from accounts.email_verif import send_verification_email
from accounts.forms import FitnessProUserCreationForm, ProfileForm, UserDeleteForm
from accounts.models import Profile, EmailVerificationToken, FitnessProUser
import logging
# Create your views here.

UserModel = get_user_model()


class FitnessProUserRegisterView(CreateView):
    model = UserModel
    form_class = FitnessProUserCreationForm
    template_name = 'accounts/register-page.html'
    success_url = reverse_lazy('accounts:login')

    def form_valid(self, form):
        response = super().form_valid(form)

        success, message = send_verification_email(self.request, self.object)
        if success:
            messages.success(self.request, 'Your account has been created successfully! Please check your email to verify your account.')
        else:
            self.object.delete()
            messages.error(self.request, 'Registration failed due to email delivery issue. Please try again.')
            return self.form_invalid(form)
        return redirect('accounts:login')

    def form_invalid(self, form):
        messages.error(self.request, 'There was an error with your registration. Please correct the errors below and try again.')
        return super().form_invalid(form)


class ProfileDetailView(LoginRequiredMixin, DetailView):
    model = Profile
    form_class = ProfileForm
    template_name = 'accounts/profile-details.html'
    context_object_name = 'profile'

    def get_object(self, queryset = None):
        return self.request.user.profile

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
        messages.success(self.request, 'Your profile has been updated successfully!')
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
        logout(request)
        messages.success(self.request, 'Your profile has been deleted successfully!')
        return response

    def get_success_url(self):
        return reverse_lazy('common:home')


class InitialLoginView(LoginView):
    template_name = 'accounts/login-page.html'

    def form_valid(self, form):
        user = form.get_user()
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
            messages.error(request, 'This verification link has expired. Please request a new one.')
            return redirect('accounts:resend-verification')

        user = token_object.user

        if user.is_email_verified:
            messages.info(request, 'Your email is already verified. Please log in.')
            return redirect('accounts:login')

        user.is_email_verified = True
        user.is_active = True
        user.save()

        token_object.delete()

        messages.success(request, 'Your email has been verified successfully! Your account is now active. You can now log in.')

        return redirect('accounts:login')


class ResendVerificationEmailView(View):

    def get(self, request):
        return render(request, 'accounts/emails/resend_verification.html')

    def post(self, request):
        email = request.POST.get('email', '').strip()

        try:
            user = FitnessProUser.objects.get(email=email, is_email_verified=False)
            if hasattr(user, 'email_verification_token'):
                token = user.email_verification_token
                if token.is_valid():
                    success, message = send_verification_email(request, user)
                else:
                    token.delete()
                    success, message = send_verification_email(request, user)
            else:
                success, message = send_verification_email(request, user)

            if success:
                messages.success(request, 'Verification email has been sent. Please check your inbox.')
                return redirect('accounts:login')
            else:
                messages.error(request, 'Failed to send verification email. Please try again later.')

        except FitnessProUser.DoesNotExist:

            logger = logging.getLogger(__name__)
            logger.warning(f"Verification email resend requested for non-existent or already verified email: {email}")

            messages.success(request, 'If an account with that email exists and is not verified, a verification email has been sent. Please check your inbox.')
            return redirect('accounts:login')

        return render(request, 'accounts/emails/resend_verification.html')