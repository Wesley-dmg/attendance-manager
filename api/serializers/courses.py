from rest_framework import serializers
from apps.courses.models import DepartmentLevel

class DepartmentLevelSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source="department.name")
    level_name = serializers.CharField(source="level.get_name_display")

    class Meta:
        model = DepartmentLevel
        fields = ["id", "department_name", "level_name"]
