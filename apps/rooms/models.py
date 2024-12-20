from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission
from django.conf import settings

User = get_user_model()

class Room(models.Model):
    """
    Représente une salle dans l'établissement scolaire.
    """
    name = models.CharField(max_length=100, unique=True, verbose_name=_("Nom de la salle"))
    capacity = models.IntegerField(verbose_name=_("Capacité"))
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
    room = models.ForeignKey(Room, on_delete=models.CASCADE, verbose_name=_("Salle"))
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_("Utilisateur"))
    reservation_date = models.DateField(verbose_name=_("Date de réservation"))
    start_time = models.TimeField(verbose_name=_("Heure de début"))
    end_time = models.TimeField(verbose_name=_("Heure de fin"))
    equipment_needed = models.TextField(verbose_name=_("Équipement requis"), blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Créé à"))

    class Meta:
        verbose_name = _("Réservation")
        verbose_name_plural = _("Réservations")
        ordering = ['reservation_date', 'start_time']

    def __str__(self):
        return _("Réservation de {room} par {user} le {date}").format(
            room=self.room.name,
            user=self.user.username,
            date=self.reservation_date
        )

    def clean(self):
        """Valide la réservation, en s'assurant qu'il n'y a pas de chevauchements et que les horaires sont corrects."""
        if self.start_time >= self.end_time:
            raise ValidationError(_("L'heure de fin doit être après l'heure de début."))

        # Vérifie les chevauchements de réservation
        conflicts = Reservation.objects.filter(
            room=self.room,
            reservation_date=self.reservation_date,
            start_time__lt=self.end_time,
            end_time__gt=self.start_time
        ).exclude(pk=self.pk)

        if conflicts.exists():
            raise ValidationError(_("La salle est déjà réservée pour cette date et ces horaires."))

    def save(self, *args, **kwargs):
        """Enregistre la réservation et met à jour la disponibilité de la salle si la réservation est réussie."""
        self.full_clean()  # Validation avant l'enregistrement
        super().save(*args, **kwargs)
        self.room.update_room_availability(False)

    def delete(self, *args, **kwargs):
        """Supprime la réservation et restaure la disponibilité de la salle si possible."""
        room = self.room
        super().delete(*args, **kwargs)
        if not Reservation.objects.filter(room=room).exists():
            room.update_room_availability(True)


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

