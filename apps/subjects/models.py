from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

from apps.common.models import DepartmentLevelSubject  # Importer correctement si déplacé

class Subject(models.Model):
    """
    Représente une matière enseignée dans le cadre d'un département et d'un niveau d'étude.
    """
    name = models.CharField(max_length=100, verbose_name=_("Nom de la matière"),unique=True)
    code = models.CharField(max_length=10, unique=True, verbose_name=_("Code de la matière"))
    
    department_levels = models.ManyToManyField('courses.DepartmentLevel', through='common.DepartmentLevelSubject', related_name='subjects', verbose_name=_("Niveaux et départements"))

    def is_assigned_to_level_and_department(self, level, department):
        """
        Vérifie si la matière est assignée à un niveau et un département spécifiques.
        """
        return self.department_levels.filter(level=level, department=department).exists()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Matière")
        verbose_name_plural = _("Matières")
        ordering = ['name']
    
    def clean(self):
        """Valide les données du modèle avant de les enregistrer."""
        if not self.code.isalnum():
            raise ValidationError(_("Le code de la matière doit être alphanumérique."))
        super().clean()


# Gestion des Permissions pour le modèle `Subject`

def create_permissions_for_subject():
    """
    Crée des permissions spécifiques pour le modèle `Subject`.
    """
    from django.contrib.contenttypes.models import ContentType
    from django.contrib.auth.models import Permission
    
    content_type = ContentType.objects.get_for_model(Subject)

    subject_permissions = [
        ('add_subject', _('Ajouter une matière')),
        ('change_subject', _('Modifier une matière')),
        ('delete_subject', _('Supprimer une matière')),
        ('view_subject', _('Voir une matière')),
    ]
    
    for codename, name in subject_permissions:
        Permission.objects.get_or_create(
            codename=codename,
            name=name,
            content_type=content_type
        )
