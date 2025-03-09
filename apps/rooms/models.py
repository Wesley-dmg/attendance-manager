from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

User = get_user_model()

class Building(models.Model):
    """
    Représente un bâtiment dans l'établissement scolaire.
    """
    name = models.CharField(max_length=100, unique=True, verbose_name=_("Nom du bâtiment"))

    class Meta:
        verbose_name = _("Bâtiment")
        verbose_name_plural = _("Bâtiments")
        ordering = ['name']

    def __str__(self):
        return self.name


class Floor(models.Model):
    """
    Représente un étage dans un bâtiment.
    """
    number = models.PositiveIntegerField(verbose_name=_("Numéro de l'étage"))
    building = models.ForeignKey(Building, on_delete=models.CASCADE, related_name="floors", verbose_name=_("Bâtiment"))

    class Meta:
        verbose_name = _("Étage")
        verbose_name_plural = _("Étages")
        ordering = ['building', 'number']
        unique_together = ('number', 'building')

    def __str__(self):
        return f"Étage {self.number} - {self.building.name}"


class Room(models.Model):
    """
    Représente une salle dans un bâtiment donné.
    """
    room_number = models.PositiveIntegerField(unique=True, verbose_name=_("Numéro de la salle"))
    floor = models.ForeignKey(Floor, on_delete=models.CASCADE, related_name="rooms", verbose_name=_("Étage"))
    building = models.ForeignKey(Building, on_delete=models.CASCADE, related_name="rooms", verbose_name=_("Bâtiment"))
    available = models.BooleanField(default=True, verbose_name=_("Disponibilité"))

    class Meta:
        verbose_name = _("Salle")
        verbose_name_plural = _("Salles")
        ordering = ['building', 'floor', 'room_number']
        unique_together = ('room_number', 'floor', 'building')

    def __str__(self):
        return f"Salle {self.room_number} - {self.floor} ({self.building})"
    
    def mark_as_unavailable(self):
        """Marquer la salle comme indisponible."""
        self.available = False
        self.save()

    def mark_as_available(self):
        """Marquer la salle comme disponible."""
        self.available = True
        self.save()

    def update_room_availability(self, availability):
        """Met à jour la disponibilité de la salle."""
        self.available = availability
        self.save()
