
from django import forms
from django.forms import ModelForm

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

        if self.instance and self.instance.pk:
            self.fields['date_display'] = forms.DateTimeField(
                initial=self.instance.date,
                disabled=True,
                label='Date',
                help_text='The date when this record was created.',
            )

