from django.apps import AppConfig


class RoomsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.rooms'



def ready(self):
    # Importer ta fonction après l'initialisation de l'application
    from .models import create_permissions_for_room_and_reservation
        
    # Appeler la fonction qui crée les permissions
    create_permissions_for_room_and_reservation()