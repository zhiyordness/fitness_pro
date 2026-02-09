from django import forms

from training.models import TrainingDay


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
