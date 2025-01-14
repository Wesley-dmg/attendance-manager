# from django.contrib import admin

# from apps.availability.models import AvailabilityRequest, AvailabilityResponse

# class AvailabilityRequestAdmin(admin.ModelAdmin):
#     list_display = ('id', 'teachers', 'created_at','subject')
#     list_filter = ('teachers','subject')
#     search_fields = ('teachers__username',)
#     actions = ['approve_requests', 'reject_requests']

#     def teacher_names(self, obj):
#         return ", ".join([teacher.username for teacher in obj.teacher.all()])  # Assuming 'teacher' is a many-to-many relationship
#     teacher_names.short_description = 'Teachers'
    
#     def approve_requests(self, request, queryset):
#         queryset.update(status='approved')
#     approve_requests.short_description = "Approuver les demandes sélectionnées"

#     def reject_requests(self, request, queryset):
#         queryset.update(status='rejected')
#     reject_requests.short_description = "Rejeter les demandes sélectionnées"

# class AvailabilityResponseAdmin(admin.ModelAdmin):
#     list_display = ('id', 'request', 'teacher', 'availability', 'status')
#     list_filter = ('status', 'teacher')
#     search_fields = ('teacher__username', 'request__id')
    
# admin.site.register(AvailabilityRequest, AvailabilityRequestAdmin)
# admin.site.register(AvailabilityResponse, AvailabilityResponseAdmin)
