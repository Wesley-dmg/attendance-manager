from django.contrib import admin
from apps.courses.models import Department, DepartmentLevel, Level

class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description')  # Afficher 'description' car il est dans le modèle
    search_fields = ('name',)
    # Aucune modification supplémentaire nécessaire

class LevelAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')  # Supprimer 'description' car il n'existe pas dans ce modèle
    search_fields = ('name',)

class DepartmentLevelAdmin(admin.ModelAdmin):
    list_display = ('id', 'department_name', 'level_name')  # Utiliser des méthodes pour afficher les noms des départements et niveaux
    search_fields = ('department__name', 'level__name')
    list_filter = ('department', 'level')

    # Méthodes personnalisées pour afficher les noms des départements et niveaux dans `list_display`
    def department_name(self, obj):
        return obj.department.name
    department_name.admin_order_field = 'department'  # Permet de trier par le champ 'department'
    department_name.short_description = 'Département'  # Nom plus lisible dans l'interface admin

    def level_name(self, obj):
        return obj.level.name
    level_name.admin_order_field = 'level'  # Permet de trier par le champ 'level'
    level_name.short_description = 'Niveau'  # Nom plus lisible dans l'interface admin

# Enregistrement des modèles avec les admins configurés
admin.site.register(Department, DepartmentAdmin)
admin.site.register(Level, LevelAdmin)
admin.site.register(DepartmentLevel, DepartmentLevelAdmin)
