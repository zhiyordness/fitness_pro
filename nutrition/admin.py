from django.contrib import admin


from nutrition.models import FoodDatabase, Meal, MealFoodItem, NutritionDay, MealCompletion, NutritionTarget


# Register your models here.
@admin.register(FoodDatabase)
class FoodDatabaseAdmin(admin.ModelAdmin):
    list_display = ['name', 'calories', 'carbohydrates', 'protein', 'fat']
    search_fields = ['name']
    list_filter = ['calories', 'carbohydrates', 'protein', 'fat']


@admin.register(Meal)
class MealAdmin(admin.ModelAdmin):
    list_display = ['name', 'day', 'time']


@admin.register(MealFoodItem)
class MealFoodItem(admin.ModelAdmin):
    list_display = ['meal' ,'food__name', 'quantity']
    search_fields = ['meal__name']
    list_filter = ['meal__name']


@admin.register(NutritionDay)
class NutritionDayAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']
    list_filter = ['name']

@admin.register(MealCompletion)
class MealCompletionAdmin(admin.ModelAdmin):
    list_display = ['user', 'meal', 'status']
    search_fields = ['meal__name']
    list_filter = ['status', 'completed_at']


@admin.register(NutritionTarget)
class NutritionTargetAdmin(admin.ModelAdmin):
    list_display = ['user', 'calories', 'protein', 'carbohydrates', 'fat']
    search_fields = ['user__email']



