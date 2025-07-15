from apps.users.models import StudentProfile
from attendance_api.models import Attendance


def should_archive_student(student: StudentProfile, threshold: int = 10):
    total_absences = Attendance.objects.filter(student=student, status="absent", archived=False).count()
    return total_absences >= threshold
