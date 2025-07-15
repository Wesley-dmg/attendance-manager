from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.subjects.models import Subject
from apps.users.models import StudentProfile, TeacherProfile
from attendance_api.models import Attendance
from attendance_api.serializers.presence import AttendanceCreateSerializer, SubjectSerializer

class TeacherSubjectsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if not user.is_teacher:
            return Response({"error": "Accès refusé. Réservé aux enseignants."}, status=403)
        
        try:
            teacher_profile = TeacherProfile.objects.get(user=user)
        except TeacherProfile.DoesNotExist:
            return Response({"error": "Profil enseignant introuvable."}, status=404)

        subjects = teacher_profile.subjects.all()
        serializer = SubjectSerializer(subjects, many=True)
        return Response(serializer.data)

class CreateAttendanceView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = AttendanceCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        user = request.user
        if not user.is_teacher:
            return Response({"error": "Seuls les enseignants peuvent enregistrer une présence."}, status=403)

        data = serializer.validated_data
        subject_id = data["subject_id"]
        department_ids = data["department_ids"]
        date = data["date"]
        absent_ids = set(data["absent_student_ids"])

        try:
            subject = Subject.objects.get(id=subject_id)
            teacher_profile = TeacherProfile.objects.get(user=user)
        except (Subject.DoesNotExist, TeacherProfile.DoesNotExist):
            return Response({"error": "Matière ou enseignant introuvable."}, status=400)

        students = StudentProfile.objects.filter(
            major__id__in=department_ids,
            archived=False  # ⚠️ important : n’inclure que les actifs
        ).select_related("user")

        created, updated = 0, 0
        for student in students:
            status = "absent" if student.id in absent_ids else "present"

            obj, is_created = Attendance.objects.get_or_create(
                student=student,
                teacher=teacher_profile,
                subject=subject,
                date=date,
                defaults={"status": status}
            )

            if not is_created and obj.status != status:
                obj.status = status
                obj.save(update_fields=["status"])
                updated += 1
            elif is_created:
                created += 1

        return Response({
            "message": f"Présence enregistrée.",
            "absents": len(absent_ids),
            "présents": students.count() - len(absent_ids),
            "créés": created,
            "modifiés": updated,
            "total": students.count()
        }, status=201)
