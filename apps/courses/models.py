from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission



class Department(models.Model):
    """
    Représente une filière dans un établissement scolaire.
    """
    name = models.CharField(max_length=100, unique=True, db_index=True, verbose_name=_('Nom'))
    description = models.TextField(blank=True, verbose_name=_('Description'))
    
    class Meta:
        ordering = ['name']
        verbose_name = _('Département')
        verbose_name_plural = _('Départements')
    
    def __str__(self):
        return self.name
        
class Level(models.Model):
    """
    Représente un niveau d'étude dans le cursus (Licence 1, Master 2, etc.).
    """
    LEVEL_CHOICES = (
        ('L1', _('Licence 1')),
        ('L2', _('Licence 2')),
        ('L3', _('Licence 3')),
        ('M1', _('Master 1')),
        ('M2', _('Master 2')),
    )

    name = models.CharField(max_length=2, choices=LEVEL_CHOICES, unique=True, verbose_name=_('Niveau'))

    class Meta:
        verbose_name = _('Niveau d\'études')
        verbose_name_plural = _('Niveaux d\'études')
    
    def __str__(self):
        return self.get_name_display()

class DepartmentLevel(models.Model):
    """
    Relation entre un département et un niveau d'étude. 
    Un département peut avoir plusieurs niveaux d'études, et un niveau peut appartenir à plusieurs départements.
    """
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='department_levels', verbose_name=_('Département'))
    level = models.ForeignKey(Level, on_delete=models.CASCADE, related_name='department_levels', verbose_name=_('Niveau'))

    class Meta:
        constraints = [
                        models.UniqueConstraint(fields=['department', 'level'], name='unique_department_level')
                    ]# Assure qu'une combinaison département-niveau est unique.
        verbose_name = _('Niveau départemental')
        verbose_name_plural = _('Niveaux départementaux')
    
    def __str__(self):
        return f'{self.level.name} - {self.department.name}'
    
    @property
    def get_full_description(self):
        return str(self)



# Gestion des Permissions

def create_permissions_for_models():
    """
    Crée des permissions spécifiques pour les modèles `Department`, `Level`, et `DepartmentLevelSubject`.
    """
    content_type_department = ContentType.objects.get_for_model(Department)
    content_type_level = ContentType.objects.get_for_model(Level)
    

    # Permissions pour le modèle `Department`
    department_permissions = [
        ('add_department', _('Ajouter un département')),
        ('change_department', _('Modifier un département')),
        ('delete_department', _('Supprimer un département')),
        ('view_department', _('Voir un département')),
    ]
    for codename, name in department_permissions:
        Permission.objects.get_or_create(
            codename=codename,
            name=name,
            content_type=content_type_department
        )

    # Permissions pour le modèle `Level`
    level_permissions = [
        ('add_level', _('Ajouter un niveau d\'étude')),
        ('change_level', _('Modifier un niveau d\'étude')),
        ('delete_level', _('Supprimer un niveau d\'étude')),
        ('view_level', _('Voir un niveau d\'étude')),
    ]
    for codename, name in level_permissions:
        Permission.objects.get_or_create(
            codename=codename,
            name=name,
            content_type=content_type_level
        )
