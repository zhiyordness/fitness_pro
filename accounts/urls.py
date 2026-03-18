from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path, include

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


]

urlpatterns = [
    path('', include(authentication)),
    path('profile/<int:pk>/', include(profile)),
]