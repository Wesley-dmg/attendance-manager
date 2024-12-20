from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission

class DepartmentLevelSubject(models.Model):
    """
    Relation entre une matière, un département et un niveau d'étude.
    Ce modèle permet d'assigner des matières à des départements et des niveaux spécifiques.
    """
    department_level = models.ForeignKey('courses.DepartmentLevel', on_delete=models.CASCADE, related_name='department_levels_subjects', verbose_name=_('Niveau Départemental'))
    subject = models.ForeignKey('subjects.Subject', on_delete=models.CASCADE, related_name='department_levels_subjects', verbose_name=_('Matière'))

    class Meta:
        unique_together = ('department_level', 'subject')  # Assure qu'une matière n'est liée qu'une seule fois à un département-niveau.
        verbose_name = _('Matière par département et niveau')
        verbose_name_plural = _('Matières par département et niveau')
    
    def get_full_description(self):
        """
        Retourne une description complète de cette matière pour un département et un niveau d'étude donnés.
        """
        return f'{self.subject.name} - Niveau: {self.department_level.level.name}, Filière: {self.department_level.department.name}'

    def __str__(self):
        return f'{self.subject.name} - {self.department_level.level.name} ({self.department_level.department.name})'

def create_permissions_for_models():
    """
    Crée des permissions spécifiques pour les modèles `Department`, `Level`, et `DepartmentLevelSubject`.
    """
    content_type_department_level_subject = ContentType.objects.get_for_model(DepartmentLevelSubject)
    
    # Permissions pour le modèle `DepartmentLevelSubject`
    department_level_subject_permissions = [
        ('add_departmentlevelsubject', _('Ajouter une matière par département et niveau')),
        ('change_departmentlevelsubject', _('Modifier une matière par département et niveau')),
        ('delete_departmentlevelsubject', _('Supprimer une matière par département et niveau')),
        ('view_departmentlevelsubject', _('Voir une matière par département et niveau')),
    ]
    for codename, name in department_level_subject_permissions:
        Permission.objects.get_or_create(
            codename=codename,
            name=name,
            content_type=content_type_department_level_subject
        )
