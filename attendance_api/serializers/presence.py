from rest_framework import serializers
from apps.subjects.models import Subject

class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ["id", "name", "code"]

class AttendanceCreateSerializer(serializers.Serializer):
    subject_id = serializers.IntegerField()
    department_ids = serializers.ListField(child=serializers.IntegerField())
    date = serializers.DateField()
    absent_student_ids = serializers.ListField(child=serializers.IntegerField())

