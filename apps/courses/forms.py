from django import forms

from apps.courses.models import Department, DepartmentLevel, Level

class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name', 'description']
        labels = {
            'name': ' Filière',
            'description': 'Description',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Entrez le nom de la filière'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Entrez la description de la filière'}),
        }

class LevelForm(forms.ModelForm):
    class Meta:
        model = Level
        fields = ['name']
        labels = {
            'name': 'Niveau d\'études',
        }
        widgets = {
            'name': forms.Select(attrs={'class': 'form-control'}),
        }

class DepartmentLevelForm(forms.ModelForm):
    class Meta:
        model = DepartmentLevel
        fields = ['department', 'level']
        labels = {
            'department': 'Filière',
            'level': 'Niveau d\'études',
        }
        widgets = {
            'department': forms.Select(attrs={'class': 'form-control'}),
            'level': forms.Select(attrs={'class': 'form-control'}),
        }
