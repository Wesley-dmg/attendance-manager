from django import forms
from django.utils import timezone

from apps.courses.models import DepartmentLevel
from apps.rooms.models import Room
from apps.subjects.models import Subject
from apps.timetable.models import TimeSlot
from apps.users.models import TeacherProfile

class CourseSessionCreationForm(forms.Form):
    # Champs pour le Timetable
    timetable_start_date = forms.DateField(
        label="Date de début", 
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    timetable_end_date = forms.DateField(
        label="Date de fin", 
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    
    # Champs pour la CourseSession
    subject = forms.ModelChoiceField(
        queryset=Subject.objects.all(), 
        label="Matière", 
        widget=forms.Select(attrs={'class': 'form-control select2'})
    )
    teacher = forms.ModelChoiceField(
        queryset=TeacherProfile.objects.all(), 
        label="Enseignant", 
        widget=forms.SelectMultiple(attrs={'class': 'form-control select2'})
    )
    department_levels = forms.ModelMultipleChoiceField(
        queryset=DepartmentLevel.objects.all(), 
        label="Fillières",
        widget=forms.SelectMultiple(attrs={'class': 'form-control select2'})
    )
    room = forms.ModelChoiceField(
        queryset=Room.objects.all(), 
        label="Salle", 
        widget=forms.Select(attrs={'class': 'form-control select2'})
    )
    
    # Pour la session, on a soit une date précise, soit la session s'applique sur toute la période
    session_date = forms.DateField(
        label="Date du cours", 
        required=False, 
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    
    # Créneau horaire : soit un existant, soit la création d'un nouveau
    timeslot = forms.ModelChoiceField(
        queryset=TimeSlot.objects.all(),
        label="Créneau horaire existant",
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    new_start_time = forms.TimeField(
        label="Heure de début (nouveau créneau)",
        required=False,
        widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'})
    )
    new_end_time = forms.TimeField(
        label="Heure de fin (nouveau créneau)",
        required=False,
        widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'})
    )
    
    # Checkbox pour appliquer la session sur toute la période
    session_for_all_days = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        required=False,
        label="La session est identique sur toute la période"
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Au chargement initial, ne pas peupler ces sélecteurs.
        self.fields['teacher'].queryset = TeacherProfile.objects.none()
        self.fields['department_levels'].queryset = DepartmentLevel.objects.none()
    
    def clean(self):
        cleaned_data = super().clean()
        timeslot = cleaned_data.get("timeslot")
        new_start_time = cleaned_data.get("new_start_time")
        new_end_time = cleaned_data.get("new_end_time")
        session_for_all_days = cleaned_data.get("session_for_all_days")
        session_date = cleaned_data.get("session_date")
        timetable_start_date = cleaned_data.get("timetable_start_date")
        timetable_end_date = cleaned_data.get("timetable_end_date")

        # Vérification des dates du planning
        if timetable_start_date and timetable_end_date:
            if timetable_start_date >= timetable_end_date:
                raise forms.ValidationError(
                    "La date de début du planning doit être antérieure à la date de fin."
                )

        # Validation des créneaux horaires
        if not timeslot and (not new_start_time or not new_end_time):
            raise forms.ValidationError(
                "Veuillez sélectionner un créneau horaire existant ou renseigner une nouvelle plage horaire."
            )

        if new_start_time and new_end_time and new_start_time >= new_end_time:
            raise forms.ValidationError(
                "L'heure de début doit être inférieure à l'heure de fin."
            )

        # Validation de la date du cours
        if not session_for_all_days and not session_date:
            raise forms.ValidationError(
                "Veuillez fournir la date du cours ou cochez la case pour générer sur toute la période."
            )
        
        return cleaned_data

class CourseSessionAdditionalForm(forms.Form):
    # Le champ timetable_id a été retiré car on le récupère via l'URL
    
    # Les autres champs pour la session
    subject = forms.ModelChoiceField(
        queryset=Subject.objects.all(), 
        label="Matière",
        widget=forms.Select(attrs={'class': 'form-control select2'})
    )
    teacher = forms.ModelMultipleChoiceField(
        queryset=TeacherProfile.objects.none(), 
        label="Enseignant",
        widget=forms.SelectMultiple(attrs={'class': 'form-control select2'})
    )
    department_levels = forms.ModelMultipleChoiceField(
        queryset=DepartmentLevel.objects.none(), 
        label="Fillières",
        widget=forms.SelectMultiple(attrs={'class': 'form-control select2'})
    )
    room = forms.ModelChoiceField(
        queryset=Room.objects.all(), 
        label="Salle",
        widget=forms.Select(attrs={'class': 'form-control select2'})
    )
    session_date = forms.DateField(
        label="Date du cours",
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    timeslot = forms.ModelChoiceField(
        queryset=TimeSlot.objects.all(),
        label="Créneau horaire existant",
        required=False,
        widget=forms.Select(attrs={'class': 'form-control select2'})
    )
    new_start_time = forms.TimeField(
        label="Heure de début (nouveau créneau)",
        required=False,
        widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'})
    )
    new_end_time = forms.TimeField(
        label="Heure de fin (nouveau créneau)",
        required=False,
        widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Au chargement, les sélecteurs "teacher" et "department_levels" sont vides
        self.fields['teacher'].queryset = TeacherProfile.objects.none()
        self.fields['department_levels'].queryset = DepartmentLevel.objects.none()
    
    def clean(self):
        cleaned_data = super().clean()
        timeslot = cleaned_data.get("timeslot")
        new_start_time = cleaned_data.get("new_start_time")
        new_end_time = cleaned_data.get("new_end_time")
        session_date = cleaned_data.get("session_date")
        
        # Vérification du créneau horaire
        if not timeslot and (not new_start_time or not new_end_time):
            raise forms.ValidationError(
                "Veuillez sélectionner un créneau horaire existant ou renseigner une nouvelle plage horaire."
            )
        if not session_date:
            raise forms.ValidationError("Veuillez fournir la date du cours.")
        return cleaned_data
