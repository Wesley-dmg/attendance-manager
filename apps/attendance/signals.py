from apps.attendance.models import Attendance
from apps.users.models import StudentProfile


def should_archive_student(student: StudentProfile, threshold: int = 5):
    total_absences = Attendance.objects.filter(
        student=student, status="absent", archived=False
    ).count()
    return total_absences >= threshold
