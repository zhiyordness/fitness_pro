
from django import forms
from django.forms import ModelForm

from nutrition.models import Meal
from progress.models import ProgresTracking


class RecordCreateForm(ModelForm):
    class Meta:
        model = ProgresTracking
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = field.label
            if field_name in ['weight', 'height']:
                field.widget.attrs['type'] = 'number'





