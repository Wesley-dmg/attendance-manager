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
        fields = ['name', 'capacity', 'available']
        labels = {
            'name': _('Nom de la salle'),
            'capacity': _('Capacité'),
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Entrez le nom de la salle')}),
            'capacity': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': _('Entrez la capacité')}),
        }

class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['room', 'reservation_date', 'start_time', 'end_time', 'equipment_needed']
        labels = {
            'room': _('Salle'),
            'reservation_date': _('Date de réservation'),
            'start_time': _('Heure de début'),
            'end_time': _('Heure de fin'),
            'equipment_needed': _('Équipement requis'),
        }
        widgets = {
            'room': forms.Select(attrs={'class': 'form-control'}),
            'reservation_date': forms.DateInput(
                attrs={'class': 'form-control', 'type': 'date'},
                format='%Y-%m-%d'
            ),
            'start_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'equipment_needed': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': _('Spécifiez l\'équipement requis')}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
    
        # Récupère l'instance pour la réservation actuelle
        if self.instance and self.instance.pk:
            current_room = self.instance.room
            if user and not user.is_staff:
                # Inclure la salle actuelle dans le queryset des salles disponibles
                self.fields['room'].queryset = Room.objects.filter(
                    Q(available=True) | Q(pk=current_room.pk)
                )
            # Définir l'ID de la salle actuelle comme valeur initiale
            self.fields['room'].initial = current_room.id  # Utiliser l'ID pour la sélection automatique

        else:
            # Si c'est une nouvelle réservation, afficher uniquement les salles disponibles
            if user and not user.is_staff:
                self.fields['room'].queryset = Room.objects.filter(available=True)

        self.fields['reservation_date'].initial = self.instance.reservation_date
        
    def clean(self):
        """Validation supplémentaire pour les dates et heures de réservation, et les conflits de réservation."""
        cleaned_data = super().clean()
        room = cleaned_data.get('room')
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        reservation_date = cleaned_data.get('reservation_date')

        # Validation : Heure de début et de fin logique
        if start_time and end_time and start_time >= end_time:
            raise forms.ValidationError(_("L'heure de fin doit être après l'heure de début."))

        # Validation : Conflits de réservation
        if room and start_time and end_time and reservation_date:
            conflicting_reservations = Reservation.objects.filter(
                room=room,
                reservation_date=reservation_date,
                start_time__lt=end_time,
                end_time__gt=start_time
            ).exclude(pk=self.instance.pk)

            if conflicting_reservations.exists():
                raise forms.ValidationError(_("La salle est déjà réservée pour cette date et ces horaires."))

    def save(self, commit=True):
        """Sauvegarde et met à jour la disponibilité de la salle."""
        instance = super().save(commit=False)
        # On n'enregistre pas la réservation immédiatement pour vérifier si l’utilisateur est admin
        if not self.instance.pk and not self.fields['room'].queryset.filter(available=True).exists():
            raise forms.ValidationError(_("Impossible de réserver car toutes les salles sont occupées pour ce créneau."))
        
        if commit:
            instance.save()
            instance.room.update_room_availability(False)
        return instance
