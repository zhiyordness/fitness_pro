
from django import forms
from django.forms import ModelForm

from common.validators import ImageValidator
from nutrition.models import Meal
from progress.models import ProgresTracking


class RecordCreateForm(ModelForm):
    class Meta:
        model = ProgresTracking
        exclude = ['owner', 'date']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = field.label
            if field_name in ['weight', 'height']:
                field.widget.attrs['type'] = 'number'

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            validator = ImageValidator()
            validator(image)
        return image




