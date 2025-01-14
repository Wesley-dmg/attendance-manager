from django.contrib import admin
from django.contrib.auth import get_user_model

from apps.users.models import CustomUser, ParentProfile, StudentProfile, TeacherProfile

class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'first_name', 'last_name', 'email', 'role', 'is_active')
    list_filter = ('role', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    filter_horizontal = ('groups', 'user_permissions')

class TeacherProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'grade', 'get_subjects')
    
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'student_id', 'enrollment_status', 'major')

class ParentProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_children_names')

# Enregistrer les modèles dans l'admin
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(TeacherProfile, TeacherProfileAdmin)
admin.site.register(StudentProfile, StudentProfileAdmin)
admin.site.register(ParentProfile, ParentProfileAdmin)
