from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView, PasswordChangeDoneView, \
    PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.urls import path, include
from django.urls import reverse_lazy
from accounts.views import FitnessProUserRegisterView, ProfileDetailView, ProfileEditView, DeleteUserView, \
    LoginRedirectView, InitialLoginView, VerifyEmailView, ResendVerificationEmailView

app_name = 'accounts'


profile = [
    path('', include(
        [
            path('details/', ProfileDetailView.as_view(), name='profile-details'),
            path('edit/', ProfileEditView.as_view(), name='profile-edit'),
            path('delete/', DeleteUserView.as_view(), name='profile-delete'),
        ]
    ))
]


authentication = [
    path('register/', FitnessProUserRegisterView.as_view(), name='register'),
    path('verify-email/<str:token>/', VerifyEmailView.as_view(), name='verify-email'),
    path('resend-verification/', ResendVerificationEmailView.as_view(), name='resend-verification'),


    path('login/', InitialLoginView.as_view(), name='login'),
    path('login-redirect/', LoginRedirectView.as_view(), name='login-redirect'),
    path('logout/', LogoutView.as_view(), name='logout'),


    path('password-change/', PasswordChangeView.as_view(
        template_name='accounts/password-change-page.html',
        success_url=reverse_lazy('accounts:password_change_done'),
    ), name='password_change'),
    path('password-change-done/', PasswordChangeDoneView.as_view(
        template_name='accounts/password-change-page-done.html'
    ), name='password_change_done'),


    path('password-reset/', PasswordResetView.as_view(
        template_name='accounts/password_reset_form.html',
        email_template_name='accounts/password_reset_email.html',
        subject_template_name='accounts/password_reset_subject.txt',
        success_url=reverse_lazy('accounts:password_reset_done'),
    ), name='password_reset'),
    path('password-reset/done/', PasswordResetDoneView.as_view(
        template_name='accounts/password_reset_done.html'
    ), name='password_reset_done'),
    path('password-reset/confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(
            template_name='accounts/password_reset_confirm.html',
            success_url=reverse_lazy('accounts:password_reset_complete'),
        ), name='password_reset_confirm'),
    path('password-reset/complete/', PasswordResetCompleteView.as_view(
            template_name='accounts/password_reset_complete.html'
        ), name='password_reset_complete'),
]

urlpatterns = [
    path('', include(authentication)),
    path('profile/<int:pk>/', include(profile)),
]

