from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.utils import timezone

class TimeSlot(models.Model):
    """
        Modèle TimeSlot (créneau horaire)
    """
    label = models.CharField(max_length=50,blank=True,help_text=_("Label généré automatiquement, ex : '08:00 - 10:00'."))
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
        self.full_clean()
        super().save(*args, **kwargs)

class SchedulePeriod(models.Model):
    """
    Période de validité commune à un ou plusieurs emplois du temps.
    """
    name = models.CharField(max_length=100,blank=True,null=True,verbose_name=_("Nom de la période"),help_text=_("Ex : Trimestre 1, Semestre 2, etc."))
    start_date = models.DateField(verbose_name=_("Date de début"))
    end_date = models.DateField(verbose_name=_("Date de fin"))

    class Meta:
        unique_together = ('start_date', 'end_date')
        verbose_name = _("Période de planification")
        verbose_name_plural = _("Périodes de planification")
        ordering = ['start_date']

    def __str__(self):
        if self.name:
            return self.name
        return f"{self.start_date.strftime('%d/%m/%Y')} - {self.end_date.strftime('%d/%m/%Y')}"

    def clean(self):
        if self.start_date > self.end_date:
            raise ValidationError(_("La date de début doit être antérieure à la date de fin."))

class Timetable(models.Model):
    """
    Modèle Timetable (emploi du temps)
    """
    department_levels = models.ManyToManyField('courses.DepartmentLevel',
        related_name='timetables',
        verbose_name=_("Départements - Niveaux"))
    period = models.ForeignKey(SchedulePeriod,
        on_delete=models.PROTECT,
        verbose_name=_("Période de planification"),
        related_name="timetables")
    year = models.PositiveIntegerField(default=timezone.now().year, verbose_name=_("Année"))

    class Meta:
        verbose_name = _("Emploi du temps")
        verbose_name_plural = _("Emplois du temps")
        ordering = ['period__start_date']
        permissions = [
            ('config_recap_semaine', _("Peut configurer et imprimer le récapitulatif de l'emploi du temps et la répartition des salles de la semaine")),
        ]

    def __str__(self):
        return f"Emploi du temps {self.year} (du {self.period.start_date} au {self.period.end_date})"

    def is_finished(self):
        """
        Retourne True si l'emploi du temps est terminé.
        """
        return timezone.now().date() > self.period.end_date

    def release_rooms(self):
        """
        Libère les salles une fois l'emploi du temps terminé.
        """
        if self.is_finished():
            for session in self.course_sessions.all():
                room = session.room
                if not room.available:
                    room.available = True
                    room.save()

class CourseSession(models.Model):
    """
    Représente une session de cours appartenant à un Timetable.
    """
    timetable = models.ForeignKey(Timetable,
        on_delete=models.CASCADE,
        related_name='course_sessions',
        verbose_name=_("Emploi du temps")
    )
    subject = models.ForeignKey('subjects.Subject',
        on_delete=models.CASCADE,
        related_name='course_sessions',
        verbose_name=_("Matière")
    )
    teacher = models.ForeignKey('users.TeacherProfile',
        on_delete=models.CASCADE,
        related_name='course_sessions',
        verbose_name=_("Enseignant")
    )
    room = models.ForeignKey('rooms.Room',
        on_delete=models.CASCADE,
        related_name='course_sessions',
        verbose_name=_("Salle")
    )
    date = models.DateField(verbose_name=_("Date du cours"))
    timeslot = models.ForeignKey(TimeSlot,
        on_delete=models.CASCADE,
        related_name='course_sessions',
        verbose_name=_("Créneau horaire")
    )

    class Meta:
        verbose_name = _("Session de cours")
        verbose_name_plural = _("Sessions de cours")
        ordering = ['date', 'timeslot__start_time']
        permissions = [
            ('view_coursesession_recap', _("Peut voir le recapitulatif de l'emplois du temps et la repartition des salles de la semaine")),   
        ]

    def __str__(self):
        return f"{self.subject.name} | {self.date.strftime('%A %d/%m/%Y')} | {self.timeslot}"

    def clean(self):
        """
        Vérifie que la date est dans la période de l'emploi du temps.
        """
        period = self.timetable.period
        if self.date < period.start_date or self.date > period.end_date:
            raise ValidationError(_("La date du cours doit être comprise dans la période de l'emploi du temps."))

    def save(self, *args, **kwargs):
        if self.room and self.pk is None:
            self.room.available = False
            self.room.save()
        super().save(*args, **kwargs)