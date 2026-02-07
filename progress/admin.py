from django.contrib import admin

from progress.models import ProgresTracking


# Register your models here.
@admin.register(ProgresTracking)
class ProgresTrackingAdmin(admin.ModelAdmin):
    list_display = ['day', 'date', 'weight', 'chest', 'shoulders', 'waist', 'biceps', 'neck', 'butt', 'tight', 'calf']
    search_fields = ['date']
    list_filter = ['date']
