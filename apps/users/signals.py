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


@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if not created:
        return

    if instance.role == "student":
        StudentProfile.objects.get_or_create(user=instance)
    elif instance.role == "teacher":
        TeacherProfile.objects.get_or_create(user=instance)
    elif instance.role == "parent":
        ParentProfile.objects.get_or_create(user=instance)
    elif instance.role == "admin":
        AdminProfile.objects.get_or_create(user=instance)
