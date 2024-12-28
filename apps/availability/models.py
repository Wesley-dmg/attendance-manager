from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings

class AvailabilityRequest(models.Model):
    """
    Demande de disponibilité pour une matière.
    """
    subject = models.ForeignKey(
        'subjects.Subject',
        on_delete=models.CASCADE,
        verbose_name=_("Matière"),
        related_name='availability_requests'
    )
    teachers = models.ManyToManyField(
        'users.TeacherProfile',
        verbose_name=_("Enseignants"),
        related_name='availability_requests',
        help_text=_("Enseignants sélectionnés pour cette demande")
    )
    days = models.JSONField(
        verbose_name=_("Jours demandés"),
        help_text=_("Liste des jours demandés au format JSON. Ex: ['lundi', 'mardi']")
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Date de création")
    )

    class Meta:
        verbose_name = _("Demande de disponibilité")
        verbose_name_plural = _("Demandes de disponibilités")
        permissions = [
            ('can_send_availability_request', _("Peut envoyer une demande de disponibilité")),
        ]

    def __str__(self):
        return f"Demande : {self.subject.name} ({self.created_at.date()})"

    def get_teachers(self):
        """
        Retourne les enseignants associés à la matière de cette demande.
        """
        return self.subject.teachers.all()  # On récupère les professeurs associés à cette matière

class AvailabilityResponse(models.Model):
    """
    Réponse d'un enseignant à une demande de disponibilité.
    """
    STATUS_CHOICES = [
        ('pending', _("En attente")),
        ('accepted', _("Accepté")),
        ('rejected', _("Rejeté")),
    ]

    request = models.ForeignKey(
        'AvailabilityRequest',
        on_delete=models.CASCADE,
        verbose_name=_("Demande"),
        related_name='responses'
    )
    teacher = models.ForeignKey(
        'users.TeacherProfile',
        on_delete=models.CASCADE,
        verbose_name=_("Enseignant"),
        related_name='availability_responses'
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name=_("Statut de la réponse")
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Dernière mise à jour")
    )

    class Meta:
        verbose_name = _("Réponse de disponibilité")
        verbose_name_plural = _("Réponses de disponibilités")
        unique_together = ('request', 'teacher')

    def __str__(self):
        return f"{self.teacher.user.username} - {self.get_status_display()} pour {self.request.subject.name}"
