from django.contrib import admin
from apps.subjects.models import Subject
from apps.courses.models import DepartmentLevel

class SubjectAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'department', 'level')
    search_fields = ('name', 'department__name', 'level__name')
    
    # Retirer 'created_at' si le champ n'existe pas dans le modèle.
    # Si tu veux le garder, ajoute un champ 'created_at' dans le modèle Subject
    # list_display = ('id', 'name', 'department', 'level')  # Si tu ne veux pas 'created_at'

    list_filter = ('department_levels__department', 'department_levels__level')  # Utilisation des relations ManyToMany pour le filtrage

    def department(self, obj):
        # Extraire le département à partir de la relation ManyToMany
        department_levels = obj.department_levels.all()
        return ", ".join([dl.department.name for dl in department_levels])
    department.short_description = 'Département'  # Label dans l'admin

    def level(self, obj):
        # Extraire les niveaux à partir de la relation ManyToMany
        department_levels = obj.department_levels.all()
        return ", ".join([dl.level.name for dl in department_levels])
    level.short_description = 'Niveau'  # Label dans l'admin

    def created_at(self, obj):
        # Si tu veux afficher une date de création
        return obj.created_at if hasattr(obj, 'created_at') else 'Non défini'
    created_at.short_description = 'Date de création'  # Label dans l'admin

admin.site.register(Subject, SubjectAdmin)
