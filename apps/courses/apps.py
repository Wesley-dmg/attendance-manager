from django.apps import AppConfig


class CoursesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.courses'


def ready(self):
    # Importer ta fonction après l'initialisation de l'application
    from .models import create_permissions_for_models

    # Appeler la fonction qui crée les permissions
    create_permissions_for_models()