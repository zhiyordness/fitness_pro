from logging import disable

from django import forms

from training.models import TrainingDay, Exercise


class SplitCreateForm(forms.ModelForm):
    class Meta:
        model = TrainingDay
        fields = '__all__'

        labels = {
            'day': 'Day',
            'description': 'Description',
            'training_muscles': 'Training Muscles',
            'exercises': 'Exercises',
        }

        widgets = {
            'description': forms.Textarea(
                attrs={
                    'placeholder': 'Enter training split description',
                    'rows': 3,
                }),
            'training_muscles': forms.SelectMultiple(
                attrs={
                    'size': 10,
                }
            ),
            'exercises': forms.SelectMultiple(
                attrs={
                    'size': 10,
                }
            ),
        }
        error_messages = {
            'day': {
                'required': 'Day is required.',
            },
            'description': {
                'required': 'Description is required.',
            },
            'training_muscles': {
                'required': 'At least one training muscle is required.',
            },
            'exercises': {
                'required': 'At least one exercise is required.',
            },
        }
        help_texts = {
            'day': 'Select the day of the week for this training split.',
            'description': 'Provide a brief description of the training split.',
            'training_muscles': 'Select the muscles that will be trained in this split.',
            'exercises': 'Select the exercises that will be included in this split.',
        }



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
