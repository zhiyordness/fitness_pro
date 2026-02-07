from django.contrib import admin

from training.models import Exercise, MuscleType, MuscleGroup, TrainingDay


# Register your models here.

@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ['name', 'sets', 'repetitions', 'type_of_muscle', 'muscles_group']
    list_filter = ['type_of_muscle__name', 'muscles_group__name']
    search_fields = ['name', 'type_of_muscle__name', 'muscles_group__name']



@admin.register(MuscleType)
class ExerciseAdmin(admin.ModelAdmin):
    ...


@admin.register(MuscleGroup)
class ExerciseAdmin(admin.ModelAdmin):
    ...


@admin.register(TrainingDay)
class ExerciseAdmin(admin.ModelAdmin):
    ...