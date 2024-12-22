from django.db.models import Q
from django import forms
from django.utils.translation import gettext_lazy as _

from apps.rooms.models import Reservation, Room

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
        fields = ['name', 'location', 'available']
        labels = {
            'name': _('Nom de la salle'),
            'location': _('Emplacement'),
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Entrez le nom de la salle')}),
                        'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Entrez l\'emplacement')}),
        }

class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['room', 'reservation_date', 'start_time', 'end_time']
        labels = {
            'room': _('Salle'),
            'reservation_date': _('Date de réservation'),
            'start_time': _('Heure de début'),
            'end_time': _('Heure de fin'),
        }
        widgets = {
            'room': forms.Select(attrs={'class': 'form-control'}),
            'reservation_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
            'start_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)  
        super().__init__(*args, **kwargs)
        
        if self.user and not self.user.is_admin:
            self.fields['room'].queryset = Room.objects.filter(available=True)

    def clean(self):
        """Appelle la logique de validation du modèle."""
        cleaned_data = super().clean()
        
        print(f"Cleaned Data: {cleaned_data}")

        room = cleaned_data.get('room')
        reservation_date = cleaned_data.get('reservation_date')
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')

        # Vérification de présence des données
        if not all([room, reservation_date, start_time, end_time]):
            raise forms.ValidationError(_("Tous les champs sont requis."))
        
        # Appel de la méthode de validation de conflit dans le modèle
        Reservation.validate_reservation_time(room, reservation_date, start_time, end_time)
        return cleaned_data             

    def save(self, commit=True):
        """Appelle la méthode du modèle pour mettre à jour la disponibilité de la salle."""
        instance = super().save(commit=False)
    
        # Log pour vérifier si l'utilisateur est bien assigné à la réservation
        print(f"Saving reservation for user: {self.user}")

        # Si la réservation est validée, mettre à jour la disponibilité de la salle
        if instance.validated:
            instance.update_room_availability()

        if commit:
            instance.save()
        return instance
