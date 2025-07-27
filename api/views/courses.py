from rest_framework.views import APIView

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.subjects.models import Subject
from api.serializers.courses import DepartmentLevelSerializer


class SubjectDepartmentsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, subject_id):
        try:
            subject = Subject.objects.get(id=subject_id)
            department_levels = subject.department_levels.all()
            serializer = DepartmentLevelSerializer(department_levels, many=True)
            return Response(serializer.data)
        except Subject.DoesNotExist:
            return Response({"error": "Matière introuvable."}, status=404)
