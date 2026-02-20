from logging import disable

from django import forms
from django.utils.translation import round_away_from_one

from training.models import TrainingDay, Exercise


class TrainingDayCreateForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['day'].widget.attrs.update({'class': 'form-control'})
        self.fields['description'].widget.attrs.update({'class': 'form-control'})

        self.fields['day'].label = 'Day'
        self.fields['description'].label = 'Description'

        self.fields['day'].help_text = 'Select the day of the week for this training split.'
        self.fields['description'].help_text = 'Provide a brief description of the training split.'

        self.fields['day'].error_messages.update({'required': 'Day is required.'})
        self.fields['description'].error_messages.update({'required': 'Description is required.'})

        self.fields['description'].widget = forms.Textarea(attrs={
            'placeholder': 'Enter training split description',
            'rows': 3,
            'class': 'form-control'
        })

    class Meta:
        model = TrainingDay
        fields = ['day', 'description']




class ExerciseCreateForm(forms.ModelForm):
    class Meta:
        model = Exercise
        exclude = ['created_on', 'updated_on']

        labels = {
            'name': 'Exercise Name',
            'sets': 'Sets',
            'repetitions': 'Repetitions',
            'video_link': 'Video Link',
            'type_of_muscle': 'Primary Muscle Type',
            'muscles_group': 'Muscle Group',
            'description': 'Description',
            'secondary_muscles': 'Secondary Muscles',
        }

        widgets = {
            'name': forms.TextInput(
                attrs={
                    'placeholder': 'Enter exercise name',
                },
            ),
            'sets': forms.NumberInput(
                attrs={
                    'placeholder': 'Enter number of sets',
                }
            ),
            'repetitions': forms.NumberInput(
                attrs={
                    'placeholder': 'Enter number of repetitions',
                }
            ),
            'video_link': forms.URLInput(
                attrs={
                    'placeholder': 'Enter video link for the exercise',
                }
            ),
            'type_of_muscle': forms.Select(),
            'muscles_group': forms.Select(),
            'description': forms.Textarea(
                attrs={
                    'placeholder': 'Enter exercise description',
                    'rows': 3,
                }
            ),
            'secondary_muscles': forms.SelectMultiple(
                attrs={
                    'size': 10,
                },
            ),
        }
        error_messages = {
            'name': {
                'required': 'Exercise name is required.',
            },
            'sets': {
                'required': 'Number of sets is required.',
                'invalid': 'Enter a valid number for sets.',
            },
            'repetitions': {
                'required': 'Number of repetitions is required.',
                'invalid': 'Enter a valid number for repetitions.',
            },
            'video_link': {
                'required': 'Video link is required.',
                'invalid': 'Enter a valid URL for the video link.',
            },
            'type_of_muscle': {
                'required': 'Primary muscle type is required.',
            },
        }
