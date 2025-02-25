from django.apps import AppConfig
from django.db.models.signals import post_migrate

class RoomsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.rooms'

    def ready(self):
        from django.core.signals import request_started
        from .signals import create_room_permissions_signal
        
        # Connecter le signal post_migrate
        post_migrate.connect(create_room_permissions_signal, sender=self)
