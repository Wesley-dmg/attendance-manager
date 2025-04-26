from django.contrib import admin
from .models import TimeSlot, SchedulePeriod, Timetable, CourseSession

@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ('label', 'start_time', 'end_time')
    list_filter = ('start_time',)
    search_fields = ('label',)
    ordering = ('start_time',)

@admin.register(SchedulePeriod)
class SchedulePeriodAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date')
    list_filter = ('start_date', 'end_date')
    search_fields = ('name',)
    ordering = ('start_date',)

@admin.register(Timetable)
class TimetableAdmin(admin.ModelAdmin):
    list_display = ('period', 'year')
    list_filter = ('year', 'period__start_date')
    search_fields = ('period__name',)
    filter_horizontal = ('department_levels',)
    ordering = ('period__start_date',)

@admin.register(CourseSession)
class CourseSessionAdmin(admin.ModelAdmin):
    list_display = ('subject', 'teacher', 'room', 'date', 'timeslot')
    list_filter = ('date', 'timeslot', 'room')
    search_fields = ('subject__name', 'teacher__user__first_name', 'teacher__user__last_name', 'room__name')
    ordering = ('date', 'timeslot__start_time')
