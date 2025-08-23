# apps/attendance/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from apps.attendance.models import Attendance
from apps.users.models import StudentProfile, StudentArchiveHistory


def should_archive_student(student: StudentProfile, threshold: int = 10):
    total_absences = Attendance.objects.filter(student=student, status="absent").count()
    return total_absences >= threshold


@receiver(post_save, sender=Attendance)
def archive_student_on_absence(sender, instance, created, **kwargs):
    """
    Dès qu'une absence est enregistrée, on vérifie si l'étudiant doit être archivé.
    """
    if created and instance.status == "absent":
        student = instance.student

        if not student.archived and should_archive_student(student):
            student.archived = True
            student.archived_at = timezone.now()
            student.save()

            # Historique
            StudentArchiveHistory.objects.create(student=student, action="archived")
