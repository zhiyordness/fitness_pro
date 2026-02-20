from django.contrib import admin

from training.models import Exercise, Muscle, MuscleGroup, TrainingDay


# Register your models here.

@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ['name', 'sets', 'repetitions']
    list_filter = ['name', 'muscles']
    search_fields = ['name', 'muscles__name']



@admin.register(Muscle)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ['name', 'group']
    list_filter = ['name', 'group']
    search_fields = ['name', 'group__name']


@admin.register(MuscleGroup)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ['name']
    list_filter = ['name']
    search_fields = ['name']


@admin.register(TrainingDay)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ['day', 'description']
    list_filter = ['day', 'muscle_groups']
    search_fields = ['day', 'description', 'muscle_groups__name']