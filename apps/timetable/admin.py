from django.contrib import admin
from apps.timetable.models import TimeSlot, Timetable, CourseSession

@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ('label', 'start_time', 'end_time')
    ordering = ('start_time',)

@admin.register(Timetable)
class TimetableAdmin(admin.ModelAdmin):
    list_display = ('start_date', 'end_date')
    ordering = ('start_date',)
    filter_horizontal = ('department_levels',)

@admin.register(CourseSession)
class CourseSessionAdmin(admin.ModelAdmin):
    list_display = ('subject', 'teacher', 'room', 'date', 'timeslot')
    ordering = ('date', 'timeslot__start_time')
    list_filter = ('date', 'timeslot')
