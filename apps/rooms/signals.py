from django.db.models.signals import post_migrate
from django.dispatch import receiver

@receiver(post_migrate)
def create_room_permissions_signal(sender, **kwargs):
    """Crée les permissions pour les salles après les migrations."""
    from .models import create_room_permissions  # Importer ici pour éviter les problèmes de chargement
    create_room_permissions()
