from datetime import timedelta
from django.utils import timezone
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
    start_date = models.DateField(
        verbose_name=_("Date de début"),
        help_text=_("Date de début de la disponibilité")
    )
    end_date = models.DateField(
        verbose_name=_("Date de fin"),
        help_text=_("Date de fin de la disponibilité")
    )
    filieres = models.ManyToManyField(
        'courses.DepartmentLevel',
        related_name='availability_requests',
        verbose_name=_("Filières")
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Date de création")
    )

    class Meta:
        verbose_name = _("Demande de disponibilité")
        verbose_name_plural = _("Demandes de disponibilités")
        permissions = [
            ('can_send_availabilityrequest', _("Peut envoyer une demande de disponibilité")),
            ('can_view_availabilityrequest_history', _("Peut voir l'historique des demande de disponibilité")),
            ('can_view_availabilityrequest_pending', _("Peut voir les demande de disponibilité en attente")),
        ]

    def __str__(self):
        return f"Demande : {self.subject.name} ({self.start_date} - {self.end_date})"

    def get_teachers(self):
        """
            Retourne les enseignants associés à la matière de cette demande.
        """
        return self.subject.teachers.all()
    
    def get_teacher_response(self, teacher):
        """
        Retourne la réponse de la demande associée à l'enseignant spécifié.
        """
        return self.responses.filter(teacher=teacher).first()
    
class AvailabilityResponse(models.Model):
    """
        Réponse d'un enseignant à une demande de disponibilité.
    """
    STATUS_CHOICES = [
        ('pending', _("En attente")),
        ('accepted', _("Accepté")),
        ('rejected', _("Rejeté")),
    ]

    request = models.ForeignKey('AvailabilityRequest',on_delete=models.CASCADE,verbose_name=_("Demande"),related_name='responses')
    teacher = models.ForeignKey('users.TeacherProfile',on_delete=models.CASCADE,verbose_name=_("Enseignant"),related_name='availability_responses')
    status = models.CharField(max_length=10,choices=STATUS_CHOICES,default='pending',verbose_name=_("Statut de la réponse"))
    updated_at = models.DateTimeField(auto_now=True,verbose_name=_("Dernière mise à jour"))

    class Meta:
        verbose_name = _("Réponse de disponibilité")
        verbose_name_plural = _("Réponses de disponibilités")
        constraints = [
                        models.UniqueConstraint(fields=['request', 'teacher'], name='unique_availability_response')
                    ]

    def __str__(self):
        return f"{self.teacher.user.username} - {self.get_status_display()} pour {self.request.subject.name}"
    