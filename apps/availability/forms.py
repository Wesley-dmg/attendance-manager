from django import forms

from apps.subjects.models import Subject

from django.utils.translation import gettext_lazy as _

from apps.users.models import TeacherProfile

class SubjectTeacherSelectionForm(forms.Form):
    """
    Formulaire pour sélectionner une matière et des enseignants.
    """
    subject = forms.ModelChoiceField(
        queryset=Subject.objects.all(),
        label=_("Matière"),
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        help_text=_("Choisissez une matière.")
    )
    teachers = forms.ModelMultipleChoiceField(
        queryset=TeacherProfile.objects.none(),
        label=_("Enseignants"),
        widget=forms.CheckboxSelectMultiple(),
        required=False,
        help_text=_("Sélectionnez un ou plusieurs enseignants.")
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'subject' in self.data:
            try:
                subject_id = int(self.data.get('subject'))
                self.fields['teachers'].queryset = TeacherProfile.objects.filter(subjects__id=subject_id)
            except (ValueError, TypeError):
                pass

class AvailabilityRequestForm(forms.Form):
    """
    Formulaire pour créer une demande de disponibilité.
    """
    subject_id = forms.IntegerField(widget=forms.HiddenInput())
    teacher_ids = forms.CharField(widget=forms.HiddenInput())  # Liste d'IDs au format CSV
    days = forms.MultipleChoiceField(
        choices=[
            ('lundi', _("Lundi")),
            ('mardi', _("Mardi")),
            ('mercredi', _("Mercredi")),
            ('jeudi', _("Jeudi")),
            ('vendredi', _("Vendredi")),
            ('samedi', _("Samedi")),
        ],
        widget=forms.CheckboxSelectMultiple,
        label=_("Jours demandés"),
        help_text=_("Cochez les jours de la semaine."),
        required=True
    )
