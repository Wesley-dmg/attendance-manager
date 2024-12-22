from django import forms
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission
from django.conf import settings

from django.utils import timezone  
# from django.db.models import Case, When, Value, IntegerField  

User = get_user_model()

class Room(models.Model):
    """
    Représente une salle dans l'établissement scolaire.
    """
    name = models.CharField(max_length=100, unique=True, verbose_name=_("Nom de la salle"))
    location = models.CharField(max_length=255, verbose_name=_("Emplacement"))
    available = models.BooleanField(default=True, verbose_name=_("Disponibilité"))

    class Meta:
        verbose_name = _("Salle")
        verbose_name_plural = _("Salles")
        ordering = ['name']

    def __str__(self):
        return self.name
    
    def mark_as_unavailable(self):
        """Marquer la salle comme indisponible."""
        self.available = False
        self.save()

    def update_room_availability(self, availability):
        """Met à jour la disponibilité de la salle."""
        self.available = availability
        self.save()

    def is_available_for(self, start_time, end_time):
        """Vérifie si la salle est disponible pour un créneau horaire donné."""
        overlapping_reservations = Reservation.objects.filter(
            room=self,
            start_time__lt=end_time,
            end_time__gt=start_time
        )
        return not overlapping_reservations.exists()

class Reservation(models.Model):
    """
     Représente une réservation pour une salle.
    """
    room = models.ForeignKey('Room', on_delete=models.CASCADE, verbose_name=_("Salle"))
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_("Utilisateur"))
    reservation_date = models.DateField(verbose_name=_("Date de réservation"))
    start_time = models.TimeField(verbose_name=_("Heure de début"))
    end_time = models.TimeField(verbose_name=_("Heure de fin"))
    # equipment_needed = models.TextField(verbose_name=_("Équipement requis"), blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Créé à"))
    validated = models.BooleanField(default=False, verbose_name=_("Validée"))
    
    class Meta:
        verbose_name = _("Réservation")
        verbose_name_plural = _("Réservations")
        ordering = ['created_at','reservation_date', 'start_time']

    def __str__(self):
        return _("Réservation de {room} par {user} le {date}").format(
            room=self.room.name,
            user=self.user.username,
            date=self.reservation_date
        )

    # def clean(self):
    #     """Validation supplémentaire pour les dates et heures de réservation, et les conflits de réservation."""
    #     cleaned_data = super().clean()
    #     print(f"Cleaned Data in Model: {cleaned_data}")  # Log pour inspecter cleaned_data
    #     room = cleaned_data.get('room')
    #     start_time = cleaned_data.get('start_time')
    #     end_time = cleaned_data.get('end_time')
    #     reservation_date = cleaned_data.get('reservation_date')

    #     # Validation : Heure de début et de fin logique
    #     if start_time and end_time and start_time >= end_time:
    #         raise ValidationError(_("L'heure de fin doit être après l'heure de début."))

    #     # Vérification des conflits de réservation
    #     conflicting_reservations = Reservation.objects.filter(
    #         room=self.room,
    #         reservation_date=self.reservation_date,
    #         start_time__lt=self.end_time,
    #         end_time__gt=self.start_time
    #     ).exclude(pk=self.pk)  # Ne pas inclure la réservation actuelle

    #     # Filtrer uniquement les réservations validées
    #     conflicting_reservations = conflicting_reservations.filter(validated=True)

    #     if conflicting_reservations.exists():
    #         raise ValidationError(_("La salle est déjà réservée pour cette date et ces horaires."))

    def clean(self):
        """Validation supplémentaire pour les dates et heures de réservation, et les conflits de réservation."""
        # Si cleaned_data est None, on l'initialise pour éviter les erreurs
        if not hasattr(self, 'cleaned_data'):
            self.cleaned_data = {}

        cleaned_data = super().clean()

        print(f"Cleaned Data in Model: {cleaned_data}")  # Log pour inspecter les données nettoyées
        room = cleaned_data.get('room')
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        reservation_date = cleaned_data.get('reservation_date')

        # Validation : Heure de début et de fin logique
        if start_time and end_time and start_time >= end_time:
            raise ValidationError(_("L'heure de fin doit être après l'heure de début."))

        # Vérification des conflits de réservation
        if room and reservation_date:
            conflicting_reservations = Reservation.objects.filter(
                room=self.room,
                reservation_date=self.reservation_date,
                start_time__lt=self.end_time,
                end_time__gt=self.start_time
            ).exclude(pk=self.pk)  # Ne pas inclure la réservation actuelle
            conflicting_reservations = conflicting_reservations.filter(validated=True)

            if conflicting_reservations.exists():
                raise ValidationError(_("La salle est déjà réservée pour cette date et ces horaires."))

        return cleaned_data

    def update_room_availability(self):
        """Met à jour la disponibilité de la salle en fonction de la réservation."""
        if self.validated:
            self.room.update_room_availability(False)
        else:
            self.room.update_room_availability(True)

    @classmethod
    def validate_reservation_time(cls, room, reservation_date, start_time, end_time):
        """Méthode de validation des conflits de réservation sans inclure l'instance en cours."""
        conflicting_reservations = cls.objects.filter(
            room=room,
            reservation_date=reservation_date,
            start_time__lt=end_time,
            end_time__gt=start_time
        ).filter(validated=True)  # Filtrer uniquement les réservations validées

        if conflicting_reservations.exists():
            raise ValidationError(_("La salle est déjà réservée pour ce créneau."))
    
    def save(self, *args, **kwargs):
        """Enregistre la réservation, mais ne met pas à jour la disponibilité de la salle tant qu'elle n'est pas validée."""
        # Si la réservation est validée, la salle devient indisponible
        if self.validated:
            self.room.update_room_availability(False)
        
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """Supprime la réservation et restaure la disponibilité de la salle si possible."""
        room = self.room
        super().delete(*args, **kwargs)
        
        # Si aucune autre réservation validée n'existe, la salle devient disponible
        if not Reservation.objects.filter(room=room, validated=True).exists():
            room.update_room_availability(True)

    def is_professor(self):
        """Retourne si l'utilisateur est un professeur (priorité dans les réservations)."""
        return self.user.groups.filter(name="Teachers").exists()

    @classmethod
    def get_priority_reservations(cls):
        """Retourne les réservations, triées par priorité : les professeurs et par date de création."""
        # Trier les réservations en donnant la priorité aux professeurs (en fonction de l'ordre de création)
        return cls.objects.order_by(
            models.Case(
                models.When(user__groups__name="Teachers", then=models.Value(0)),
                default=models.Value(1),
                output_field=models.IntegerField()
            ),
            'created_at'
        )
    
    def handle_expired_reservation(self):
        """Vérifie si la réservation est passée, si oui, la salle devient disponible."""
        if self.reservation_date < timezone.now().date() or (
            self.reservation_date == timezone.now().date() and self.end_time <= timezone.now().time()):
            # La réservation est terminée, donc la salle devient disponible
            self.room.update_room_availability(True)
            # La réservation est terminée
            self.validated = False  # Optionnel : marquer la réservation comme terminée
            self.save()

# Gestion des Permissions

def create_permissions_for_room_and_reservation():
    """
    Crée des permissions spécifiques pour les modèles `Room` et `Reservation`.
    """
    content_type_room = ContentType.objects.get_for_model(Room)
    content_type_reservation = ContentType.objects.get_for_model(Reservation)

    # Permissions pour le modèle `Room`
    room_permissions = [
        ('add_room', _('Ajouter une salle')),
        ('change_room', _('Modifier une salle')),
        ('delete_room', _('Supprimer une salle')),
        ('view_room', _('Voir une salle')),
    ]
    for codename, name in room_permissions:
        Permission.objects.get_or_create(
            codename=codename,
            name=name,
            content_type=content_type_room
        )

    # Permissions pour le modèle `Reservation`
    reservation_permissions = [
        ('add_reservation', _('Ajouter une réservation')),
        ('change_reservation', _('Modifier une réservation')),
        ('delete_reservation', _('Supprimer une réservation')),
        ('view_reservation', _('Voir une réservation')),
    ]
    for codename, name in reservation_permissions:
        Permission.objects.get_or_create(
            codename=codename,
            name=name,
            content_type=content_type_reservation
        )

