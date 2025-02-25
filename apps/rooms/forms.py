from django import forms
from django.utils.translation import gettext_lazy as _
from apps.rooms.models import Room 

class RoomForm(forms.ModelForm):
    AVAILABLE_CHOICES = [
        (True, _('Oui')),
        (False, _('Non')),
    ]
    
    available = forms.ChoiceField(
        choices=AVAILABLE_CHOICES,
        widget=forms.RadioSelect(attrs={
            'class': 'Wcss flex-nowrap mx-2'
        }),
        label=_('Disponibilité'),
    )

    class Meta:
        model = Room
        fields = ['room_number', 'building', 'floor', 'available']
        labels = {
            'room_number': _('Numéro de la salle'),
            'building': _('Bâtiment'),
            'floor': _('Étage'),
        }
        widgets = {
            'room_number': forms.NumberInput(attrs={
                'class': 'form-control', 
                'placeholder': _('Entrez le numéro de la salle')
            }),
            'building': forms.Select(attrs={'class': 'form-control'}),
            'floor': forms.Select(attrs={'class': 'form-control'}),
        }
