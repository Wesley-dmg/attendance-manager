
from django import forms

from apps.subjects.models import Subject


class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['name', 'code']
        labels = {
            'name': 'Nom de la matière',
            'code': 'Code de la matière',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Entrez le nom de la matière'}),
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Entrez le code de la matière'}),
        }

