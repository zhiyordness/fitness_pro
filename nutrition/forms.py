from django.forms import ModelForm

from choices import WeekDaysChoices
from nutrition.models import Meal, FoodDatabase, MealFoodItem, NutritionDay


class MealForm(ModelForm):
    class Meta:
        model = Meal
        exclude = ['day', 'order']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = field.label



class MealFoodItemForm(ModelForm):
    class Meta:
        model = MealFoodItem
        exclude = ['meal']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = field.label



class NutritionDayForm(ModelForm):

    class Meta:
        model = NutritionDay
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = field.label



class FoodDatabaseForm(ModelForm):
    class Meta:
        model = FoodDatabase
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = field.label



class DayCreateForm(ModelForm):
    class Meta:
        model = NutritionDay
        fields = ['name']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if self.user:
            existing_days = NutritionDay.objects.filter(
                owner=self.user
            ).values_list('name', flat=True)

            self.fields['name'].choices = [
                choice for choice in WeekDaysChoices.choices
                if choice[0] not in existing_days
            ]



