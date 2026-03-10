from django.contrib import admin

from accounts.models import FitnessProUser, Profile


# Register your models here.
@admin.register(FitnessProUser)
class FitnessProUserAdmin(admin.ModelAdmin):
    list_display = ['email', 'first_name', 'last_name', 'is_staff', 'is_active']
    search_fields = ['email', 'first_name', 'last_name']
    ordering = ['first_name']


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'gender', 'fitness_goal', 'activity_level', 'experience_level']
    search_fields = ['user__email', 'user__first_name', 'user__last_name']
    ordering = ['user__first_name']
