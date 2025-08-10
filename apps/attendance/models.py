from django.db import models
from django.utils import timezone

from apps.subjects.models import Subject
from apps.users.models import StudentProfile, TeacherProfile


class Attendance(models.Model):
    STATUS_CHOICES = [
        ("present", "Présent"),
        ("absent", "Absent"),
        ("justified", "Justifié"),
    ]

    teacher = models.ForeignKey(
        TeacherProfile, on_delete=models.CASCADE, related_name="attendances"
    )
    student = models.ForeignKey(
        StudentProfile, on_delete=models.CASCADE, related_name="attendances"
    )
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    date = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)

    class Meta:
        unique_together = ("student", "subject", "date")
        ordering = ["-date"]

    def __str__(self):
        return f"{self.student} - {self.subject} - {self.status}"
