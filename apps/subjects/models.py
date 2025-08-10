from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError


class Subject(models.Model):
    """
    Représente une matière enseignée dans le cadre d'un département et d'un niveau d'étude.
    """

    name = models.CharField(
        max_length=100, verbose_name=_("Nom de la matière"), unique=True
    )
    code = models.CharField(
        max_length=10, unique=True, verbose_name=_("Code de la matière")
    )

    department_levels = models.ManyToManyField(
        "courses.DepartmentLevel",
        through="common.DepartmentLevelSubject",
        related_name="subjects",
        verbose_name=_("Niveaux et départements"),
    )

    def is_assigned_to_level_and_department(self, level, department):
        """
        Vérifie si la matière est assignée à un niveau et un département spécifiques.
        """
        return self.department_levels.filter(
            level=level, department=department
        ).exists()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Matière")
        verbose_name_plural = _("Matières")
        ordering = ["name"]

    def clean(self):
        """Valide les données du modèle avant de les enregistrer."""
        if not self.code.isalnum():
            raise ValidationError(_("Le code de la matière doit être alphanumérique."))
        super().clean()

    def save(self, *args, **kwargs):
        if self.name:
            self.name = self.name.capitalize()
        super().save(*args, **kwargs)
