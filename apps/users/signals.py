# apps/users/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import (
    CustomUser,
    StudentProfile,
    TeacherProfile,
    ParentProfile,
    AdminProfile,
)
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if not created:
        return

    # Ne pas créer de profil étudiant pour les superusers
    if instance.is_superuser:
        # Mais créer un profil admin
        AdminProfile.objects.get_or_create(user=instance)
        logger.info(f"[Signal] Profil ADMIN SUPERUSER créé pour {instance}")
        return

    if instance.role == "student":
        StudentProfile.objects.get_or_create(user=instance)
        logger.info(f"[Signal] Profil ÉTUDIANT créé pour {instance}")
    elif instance.role == "teacher":
        TeacherProfile.objects.get_or_create(user=instance)
        logger.info(f"[Signal] Profil ENSEIGNANT créé pour {instance}")
    elif instance.role == "parent":
        ParentProfile.objects.get_or_create(user=instance)
        logger.info(f"[Signal] Profil PARENT créé pour {instance}")
    elif instance.role == "admin":
        AdminProfile.objects.get_or_create(user=instance)
        logger.info(f"[Signal] Profil ADMIN créé pour {instance}")
