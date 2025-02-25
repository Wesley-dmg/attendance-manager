from django.contrib import admin
from .models import AvailabilityRequest, AvailabilityResponse

@admin.register(AvailabilityRequest)
class AvailabilityRequestAdmin(admin.ModelAdmin):
    list_display = ('subject', 'start_date', 'end_date', 'created_at', 'get_teachers_list')
    list_filter = ('start_date', 'end_date', 'subject', 'filieres')
    search_fields = ('subject__name', 'teachers__user__username')
    date_hierarchy = 'start_date'
    filter_horizontal = ('teachers', 'filieres')

    def get_teachers_list(self, obj):
        return ", ".join([teacher.user.username for teacher in obj.teachers.all()])
    get_teachers_list.short_description = "Enseignants"

@admin.register(AvailabilityResponse)
class AvailabilityResponseAdmin(admin.ModelAdmin):
    list_display = ('request', 'teacher', 'status', 'updated_at')
    list_filter = ('status', 'updated_at')
    search_fields = ('teacher__user__username', 'request__subject__name')
    date_hierarchy = 'updated_at'
