from django import forms
from django.forms import ModelForm

from nutrition.models import Meal, FoodDatabase, MealFoodItem


class MealForm(ModelForm):
    class Meta:
        model = Meal
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = field.label

