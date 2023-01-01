from django import forms
from apps.common.models import DepartmentLevelSubject


class DepartmentLevelSubjectForm(forms.ModelForm):
    class Meta:
        model = DepartmentLevelSubject
        fields = ['department_level', 'subject']
        labels = {
            'department_level': ' Filière',
            'subject': 'Matière',
        }
        widgets = {
            'department_level': forms.Select(attrs={'class': 'form-control select2'}),
            'subject': forms.Select(attrs={'class': 'form-control select2'}),
        }
