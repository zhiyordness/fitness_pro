from django.contrib import admin

from training.models import Exercise, Muscle, MuscleGroup, TrainingDay, PersonalRecord, WorkoutSession


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
    list_display = ['owner', 'day', 'description']
    list_filter = ['day', 'muscle_groups']
    search_fields = ['day', 'description', 'muscle_groups__name']


@admin.register(PersonalRecord)
class PersonalRecordAdmin(admin.ModelAdmin):
    list_display = ['owner', 'exercise', 'workout_set', 'weight', 'repetitions', 'achieved_at']


@admin.register(WorkoutSession)
class WorkoutSessionAdmin(admin.ModelAdmin):
    list_display = ['owner', 'status', 'started_at', 'finished_at']