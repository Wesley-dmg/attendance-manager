from django.utils import timezone
from apps.users.models import StudentArchiveHistory, StudentProfile
from api.serializers.students import StudentSerializer
from rest_framework.response import Response

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated


class StudentsByDepartmentsView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        department_ids = request.data.get("department_ids", [])
        if not isinstance(department_ids, list) or not department_ids:
            return Response({"error": "Liste de filières invalide."}, status=400)

        students = (
            StudentProfile.objects.filter(major__id__in=department_ids, archived=False)
            .select_related("user")
            .order_by("user__last_name")
        )
        serializer = StudentSerializer(students, many=True)
        return Response(serializer.data)


def archive_student(student, reason="Trop d’absences"):
    student.archived = True
    student.archived_at = timezone.now()
    student.archived_reason = reason
    student.save(update_fields=["archived", "archived_at", "archived_reason"])

    StudentArchiveHistory.objects.create(
        student=student, action="archived", reason=reason
    )


def unarchive_student(student, reason="Réintégration manuelle"):
    student.archived = False
    student.archived_at = None
    student.archived_reason = None
    student.save(update_fields=["archived", "archived_at", "archived_reason"])

    StudentArchiveHistory.objects.create(
        student=student, action="unarchived", reason=reason
    )
