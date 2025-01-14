from django.contrib import admin

from apps.common.models import DepartmentLevelSubject

from apps.courses.models import DepartmentLevel
from apps.subjects.models import Subject

class DepartmentLevelSubjectAdmin(admin.ModelAdmin):
    list_display = ('subject', 'department_level', 'get_full_description')
    search_fields = ('subject__name', 'department_level__department__name', 'department_level__level__name')
    list_filter = ('department_level__department', 'department_level__level')
    ordering = ('department_level__department', 'department_level__level', 'subject')
    
    # Affichage du détail de la description complète dans la liste admin
    def get_full_description(self, obj):
        return obj.get_full_description()
    get_full_description.short_description = 'Description complète'

# Enregistrer le modèle `DepartmentLevelSubject` dans l'admin
admin.site.register(DepartmentLevelSubject, DepartmentLevelSubjectAdmin)
