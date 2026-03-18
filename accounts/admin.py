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
        (_("Personal info"), {"fields": ("email",)}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "is_email_verified",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "registration_date")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "usable_password", "password1", "password2"),
            },
        ),
    )

    def get_first_name(self, obj):
        try:
            return obj.profile.first_name
        except Profile.DoesNotExist:
            return "—"
    get_first_name.short_description = 'First Name'
    get_first_name.admin_order_field = 'profile__first_name'

    def get_last_name(self, obj):
        try:
            return obj.profile.last_name
        except Profile.DoesNotExist:
            return "—"
    get_last_name.short_description = 'Last Name'
    get_last_name.admin_order_field = 'profile__last_name'

    list_display = ['email', 'get_first_name', 'get_last_name', 'is_staff', 'is_active', 'is_email_verified']
    search_fields = ['email', 'profile__first_name', 'profile__last_name']
    ordering = ['email']
    list_filter = ['is_staff', 'is_active', 'is_superuser', 'is_email_verified', 'groups']


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user_email', 'first_name', 'last_name', 'gender', 'fitness_goal', 'activity_level', 'experience_level']
    search_fields = ['user__email', 'first_name', 'last_name']
    ordering = ['first_name']
    list_filter = ['gender', 'fitness_goal', 'activity_level', 'experience_level']
    raw_id_fields = ['user']

    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'Email'
    user_email.admin_order_field = 'user__email'

