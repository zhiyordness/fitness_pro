from django.contrib import messages
from django.contrib.auth import get_user_model, logout, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, UpdateView, DeleteView, RedirectView

from accounts.forms import FitnessProUserCreationForm, ProfileForm, UserDeleteForm
from accounts.models import Profile

# Create your views here.

UserModel = get_user_model()


class FitnessProUserRegisterView(CreateView):
    model = UserModel
    form_class = FitnessProUserCreationForm
    template_name = 'accounts/register-page.html'
    success_url = reverse_lazy('accounts:login')


class ProfileDetailView(LoginRequiredMixin, DetailView):
    model = Profile
    form_class = ProfileForm
    template_name = 'accounts/profile-details.html'

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