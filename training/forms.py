

from django import forms

from choices import WeekDaysChoices
from training.models import TrainingDay, Exercise, TrainingDayExercise, WorkoutSet


class TrainingDayCreateForm(forms.ModelForm):

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)

        if user:
            used_days = TrainingDay.objects.filter(
                owner=user
            ).values_list(
                'day',
                flat=True,
            )

            self.fields['day'].choices = [
                choice
                for choice in WeekDaysChoices.choices
                if choice[0] not in used_days
            ]

    class Meta:
        model = TrainingDay
        fields = ['day', 'description']
        widgets = {
            'day': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Enter training day description'}),
        }
        labels = {
            'day': 'Training Day',
            'description': 'Description',
        }
        help_texts = {
            'description': 'Provide a brief description of the training day.',

        }
        error_messages = {
            'day': {
                'required': 'Please select a training day.',
                'invalid_choice': 'Please select a valid training day.',
            },
            'description': {
                'required': 'Please provide a description for the training day.',
                'max_length': 'Description cannot exceed 300 characters.',
            },
        }



class ExerciseCreateForm(forms.ModelForm):
    class Meta:
        model = Exercise
        fields = ['name', 'muscles', 'sets', 'repetitions', 'video_link']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'e.g. Bench Press',}),
            'muscles': forms.SelectMultiple(attrs={
                'class': 'form-control', 'size': 10,
                'help_text': 'Hold down "Control", or "Command" on a Mac, to select more than one.'}),
            'sets': forms.NumberInput(attrs={
                'class': 'form-control', 'placeholder': 'e.g. 3', 'min': 1}),
            'repetitions': forms.NumberInput(attrs={
                'class': 'form-control', 'placeholder': 'e.g. 10', 'min': 1}),
            'video_link': forms.URLInput(attrs={
                'class': 'form-control', 'placeholder': 'e.g. https://www.youtube.com/...'}),
        }

        labels = {
            'name': 'Exercise Name',
            'muscles': 'Target Muscles',
            'sets': 'Number of Sets',
            'repetitions': 'Number of Repetitions',
            'video_link': 'Video Tutorial Link',
        }
        help_texts = {
            'sets': 'Recommended: 3-4 sets per exercise.',
            'repetitions': 'Recommended: 8-12 repetitions for muscle growth, 12-15 for endurance.',
        }
        error_messages = {
            'name': {
                'required': 'Please enter the name of the exercise.',
                'max_length': 'Exercise name cannot exceed 100 characters.',
            },
            'sets': {
                'required': 'Please enter the number of sets.',
                'min_value': 'Number of sets must be at least 1.',
            },
            'repetitions': {
                'required': 'Please enter the number of repetitions.',
                'min_value': 'Number of repetitions must be at least 1.',
            },
        }



class TrainingDayExerciseForm(forms.ModelForm):

    class Meta:
        model = TrainingDayExercise
        fields = [
            'custom_sets',
            'custom_repetitions',
        ]

        widgets = {
            'custom_sets': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'min': 1,
                }
            ),
            'custom_repetitions': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'min': 1,
                }
            ),
        }

        labels = {
            'custom_sets': 'Sets',
            'custom_repetitions': 'Repetitions',
        }


class WorkoutSetEditForm(forms.ModelForm):

    class Meta:
        model = WorkoutSet

        fields = (
            'weight',
            'repetitions',
        )