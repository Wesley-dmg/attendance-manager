# apps/users/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import (
    CustomUser,
    StudentProfile,
    TeacherProfile,
    ParentProfile,
    AdminProfile,
    Role,
)
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if not created:
        return

    # Ne pas créer de profil étudiant pour les superusers
    if instance.is_superuser:
        admin_profile, _ = AdminProfile.objects.get_or_create(user=instance)
        logger.info(f"[Signal] Profil ADMIN SUPERUSER créé pour {instance}")
        return

    # Récupère tous les rôles de l'utilisateur
    roles = list(instance.role.values_list("name", flat=True))

    if "student" in roles:
        StudentProfile.objects.get_or_create(user=instance)
        logger.info(f"[Signal] Profil ÉTUDIANT créé pour {instance}")

    if "teacher" in roles:
        TeacherProfile.objects.get_or_create(user=instance)
        logger.info(f"[Signal] Profil ENSEIGNANT créé pour {instance}")

    if "parent" in roles:
        ParentProfile.objects.get_or_create(user=instance)
        logger.info(f"[Signal] Profil PARENT créé pour {instance}")

    if "admin" in roles:
        AdminProfile.objects.get_or_create(user=instance)
        logger.info(f"[Signal] Profil ADMIN créé pour {instance}")
