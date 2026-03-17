from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from unfold.admin import ModelAdmin
from unfold.forms import AdminPasswordChangeForm
from django.utils.translation import gettext_lazy as _
from accounts.forms import FitnessProUserCreationForm, FitnessProUserChangeForm
from accounts.models import Profile

admin.site.unregister(Group)

UserModel = get_user_model()
# Register your models here.


@admin.register(UserModel)
class FitnessProUserAdmin(BaseUserAdmin, ModelAdmin):
    model = UserModel
    form = FitnessProUserChangeForm
    add_form = FitnessProUserCreationForm
    change_password_form = AdminPasswordChangeForm

    fieldsets = (
        (None, {"fields": ("password",)}),
        (_("Personal info"), {"fields": ("email", "first_name", "last_name")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login",)}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "first_name", "last_name", "usable_password", "password1", "password2"),
            },
        ),
    )

    list_display = ['email', 'first_name', 'last_name', 'is_staff', 'is_active']
    search_fields = ['email', 'first_name', 'last_name']
    ordering = ['first_name']


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'gender', 'fitness_goal', 'activity_level', 'experience_level']
    search_fields = ['user__email', 'user__first_name', 'user__last_name']
    ordering = ['user__first_name']
