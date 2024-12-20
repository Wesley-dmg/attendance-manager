from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.core.exceptions import ValidationError
from datetime import timedelta

class AvailabilityManager(models.Manager):
    def current_and_future_availability(self, professor):
        """
        Retrieve current and future availability for a professor.
        :param professor: The teacher for whom to retrieve availability.
        :return: QuerySet of availabilities for the current and future weeks.
        """
        today = timezone.now().date()
        start_of_month = today.replace(day=1)
        end_of_month = (start_of_month + timedelta(days=31)).replace(day=1) - timedelta(days=1)

        return self.filter(
            professor=professor,
            created_at__date__gte=today,
            created_at__date__lte=end_of_month
        ).order_by('day_of_week', 'start_time')

class Availability(models.Model):
    """
    Modèle pour gérer les disponibilités des professeurs avec des dates spécifiques.
    """

    # L'utilisateur (professeur) associé
    professor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='availabilities',
        verbose_name=_("Professeur")
    )

    # Date spécifique de la disponibilité
    date = models.DateField(verbose_name=_("Date"))

    # Heures de début et de fin
    start_time = models.TimeField(verbose_name=_("Heure de début"))
    end_time = models.TimeField(verbose_name=_("Heure de fin"))

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Créé le"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Mis à jour le"))

    class Meta:
        verbose_name = _("Disponibilité")
        verbose_name_plural = _("Disponibilités")
        ordering = ['date', 'start_time']
        constraints = [
            models.UniqueConstraint(
                fields=['professor', 'date', 'start_time', 'end_time'],
                name='unique_availability_per_professor'
            )
        ]

    def __str__(self):
        """
        Représentation textuelle d'une disponibilité.
        """
        return f"{self.professor.username} - {self.date} ({self.start_time} - {self.end_time})"

    def clean(self):
        """
        Valider les contraintes avant de sauvegarder :
        - L'heure de début doit être avant l'heure de fin.
        - Les disponibilités ne doivent pas se chevaucher pour un même professeur à la même date.
        """
        if self.start_time >= self.end_time:
            raise ValidationError(_("L'heure de début doit être avant l'heure de fin."))

        overlapping_availability = Availability.objects.filter(
            professor=self.professor,
            date=self.date
        ).exclude(pk=self.pk).filter(
            start_time__lt=self.end_time,
            end_time__gt=self.start_time
        )
        if overlapping_availability.exists():
            raise ValidationError(_("Les disponibilités ne doivent pas se chevaucher."))

    def save(self, *args, **kwargs):
        """
        Sauvegarder l'objet avec la validation.
        """
        self.full_clean()  # Appelle la méthode clean pour valider avant sauvegarde.
        super().save(*args, **kwargs)

