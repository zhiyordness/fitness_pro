from datetime import date

from django import forms
from django.contrib.auth import get_user_model, authenticate
from unfold.forms import UserChangeForm, UserCreationForm

from accounts.models import Profile
from common.validators import ImageValidator

UserModel = get_user_model()


class FitnessProUserCreationForm(UserCreationForm):

    class Meta:
        model = UserModel
        fields = ["email",]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'usable_password' in self.fields:
            del self.fields['usable_password']

    def save(self, commit=True):
        user = super().save(commit=commit)

        if commit:
            Profile.objects.get_or_create(user=user)
        return user

class FitnessProUserChangeForm(UserChangeForm):
    class Meta:
        model = UserModel
        fields = '__all__'




class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        exclude = ['user']

        labels = {
            'first_name': 'First Name',
            'last_name': 'Last Name',
            'gender': 'Gender',
            'date_of_birth': 'Date of Birth',
            'height': 'Height (cm)',
            'target_weight': 'Target Weight (kg)',
            'fitness_goal': 'Fitness Goal',
            'activity_level': 'Activity Level',
            'experience_level': 'Experience Level',
            'bio': 'Bio',
            'profile_picture': 'Profile Picture',
        }
        widgets = {
            'date_of_birth': forms.SelectDateWidget(
                years=range(1950, date.today().year + 1),
            )
        }

    def clean_image(self):
        profile_picture = self.cleaned_data.get('profile_picture')
        if profile_picture:
            validator = ImageValidator()
            validator(profile_picture)
        return profile_picture


class UserDeleteForm(forms.Form):
    password = forms.CharField(
        widget=forms.PasswordInput,
        label="Confirm Password",
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if not authenticate(email=self.user.email, password=password):
            raise forms.ValidationError("Incorrect password. Please try again.")
        return password