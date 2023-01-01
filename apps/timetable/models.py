from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.utils import timezone


class TimeSlot(models.Model):
    """
        Modèle TimeSlot (créneau horaire)
    """
    label = models.CharField(
        max_length=50,
        blank=True,
        help_text=_("Label généré automatiquement, ex : '08:00 - 10:00'.")
    )
    start_time = models.TimeField(verbose_name=_("Heure de début"))
    end_time = models.TimeField(verbose_name=_("Heure de fin"))

    class Meta:
        unique_together = ('start_time', 'end_time')
        verbose_name = _("Créneau horaire")
        verbose_name_plural = _("Créneaux horaires")
        ordering = ['start_time']

    def __str__(self):
        return self.label or f"{self.start_time.strftime('%H:%M')} - {self.end_time.strftime('%H:%M')}"

    def clean(self):
        if self.start_time >= self.end_time:
            raise ValidationError(_("L'heure de début doit être antérieure à l'heure de fin."))

    def save(self, *args, **kwargs):
        if not self.label:
            self.label = f"{self.start_time.strftime('%H:%M')} - {self.end_time.strftime('%H:%M')}"
        super().save(*args, **kwargs)

class Timetable(models.Model):
    """
    Modèle Timetable (emploi du temps)
    """
    department_levels = models.ManyToManyField(
        'courses.DepartmentLevel',
        related_name='timetables',
        verbose_name=_("Départements - Niveaux")
    )
    start_date = models.DateField(verbose_name=_("Date de début"))
    end_date = models.DateField(verbose_name=_("Date de fin"))

    class Meta:
        verbose_name = _("Emploi du temps")
        verbose_name_plural = _("Emplois du temps")
        ordering = ['start_date']
        permissions = [
            ('config_recap_semaine', _("Peut configurer et imprimer le recapitulatif de l'emplois du temps et la repartition des salles de la semaine")),
        ]

    def __str__(self):
        return f"Emploi du temps (du {self.start_date} au {self.end_date})"

    def clean(self):
        if self.start_date > self.end_date:
            raise ValidationError(_("La date de début doit être antérieure à la date de fin."))

    def is_finished(self):
        """
        Retourne True si l'emploi du temps est terminé (la date actuelle est postérieure à end_date).
        """
        return timezone.now().date() > self.end_date

    def release_rooms(self):
        """
        Parcourt toutes les sessions associées à ce Timetable et 
        marque la salle associée comme disponible si l'emploi du temps est terminé.
        Cette méthode doit être appelée par une tâche planifiée ou une vue spécifique.
        """
        if self.is_finished():
            for session in self.course_sessions.all():
                room = session.room
                # On ne réactive la disponibilité que si la salle est actuellement marquée indisponible
                if not room.available:
                    room.available = True
                    room.save()

class CourseSession(models.Model):
    """
    Représente une session de cours appartenant à un Timetable.
    """
    timetable = models.ForeignKey(
        Timetable,
        on_delete=models.CASCADE,
        related_name='course_sessions',
        verbose_name=_("Emploi du temps")
    )
    subject = models.ForeignKey(
        'subjects.Subject',
        on_delete=models.CASCADE,
        related_name='course_sessions',
        verbose_name=_("Matière")
    )
    teacher = models.ForeignKey(
        'users.TeacherProfile',
        on_delete=models.CASCADE,
        related_name='course_sessions',
        verbose_name=_("Enseignant")
    )
    room = models.ForeignKey(
        'rooms.Room',
        on_delete=models.CASCADE,
        related_name='course_sessions',
        verbose_name=_("Salle")
    )
    date = models.DateField(verbose_name=_("Date du cours"))
    timeslot = models.ForeignKey(
        TimeSlot,
        on_delete=models.CASCADE,
        related_name='course_sessions',
        verbose_name=_("Créneau horaire")
    )

    class Meta:
        verbose_name = _("Session de cours")
        verbose_name_plural = _("Sessions de cours")
        ordering = ['date', 'timeslot__start_time']
        # unique_together = ('timetable', 'timeslot')  # Chaque TimeSlot n'est utilisé qu'une fois par Timetable

    def __str__(self):
        return f"{self.subject.name} | {self.date.strftime('%A %d/%m/%Y')} | {self.timeslot}"

    def clean(self):
        """
        Vérifier que la date est dans la période du Timetable.
        """
        if self.date < self.timetable.start_date or self.date > self.timetable.end_date:
            raise ValidationError(_("La date du cours doit être comprise dans la période de l'emploi du temps."))

    def save(self, *args, **kwargs):
        # Logique métier pour la salle :
        # Dès qu'une salle est attribuée à une session, on peut la marquer indisponible.
        # Cette logique peut également être gérée via un signal.
        if self.room and self.pk is None:  # Au moment de la création
            self.room.available = False
            self.room.save()
        super().save(*args, **kwargs)
