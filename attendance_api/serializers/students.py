from rest_framework import serializers
from apps.users.models import StudentProfile

class StudentSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = StudentProfile
        fields = ["id", "student_id", "full_name"]

    def get_full_name(self, obj):
        return f"{obj.user.last_name} {obj.user.first_name}"
