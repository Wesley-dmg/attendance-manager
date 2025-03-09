from django.contrib.auth.models import AbstractUser, Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.dispatch import receiver

from django.core.validators import RegexValidator

from apps.courses.models import DepartmentLevel
from apps.subjects.models import Subject
# from django.db.models.signals import post_migrate
# from django.dispatch import receiver
from django.db import transaction
from django.apps import apps

phone_number_validator = RegexValidator(
    regex=r'^(?:\+229|00229|\d{10})[\s-]?(\d{2,})[\s-]?(\d{2,})[\s-]?(\d{2,})[\s-]?(\d{2,})[\s-]?(\d{2,})$',
    message='Numéro de téléphone non valide.'
)

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('student', _('Étudiant')),
        ('teacher', _('Enseignant')),
        ('parent', _('Parent')),
        ('admin', _('Administrateur')),
    )
    
    GENDER_CHOICES = [
        ('male', _('Masculin')),
        ('female', _('Féminin')),
        ('other', _('Autre')),
    ]
    
    # national_id = models.CharField(max_length=20, unique=True, null=True, blank=True, db_index=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, verbose_name=_('Rôle'))
    phone_number = models.CharField(max_length=15, blank=True, validators=[phone_number_validator], verbose_name=_('Numéro de téléphone'))    
    date_of_birth = models.DateField(null=True, blank=True, verbose_name=_('Date de naissance'))
    address = models.CharField(max_length=255, blank=True, verbose_name=_('Adresse'))
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True, db_index=True, verbose_name=_('Photo de profil'))
    date_joined = models.DateTimeField(auto_now_add=True, verbose_name=_('Date d’inscription'))
    last_login = models.DateTimeField(null=True, blank=True, verbose_name=_('Dernier login'))
    preferred_contact_method = models.CharField(max_length=20, choices=[
        ('email', _('Email')),
        ('sms', _('SMS')),
        ('none', _('Aucun')),
    ], default='email', verbose_name=_('Méthode de contact préférée'))
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, null=True, blank=True, verbose_name=_('Genre'))
    
    password_updated_at = models.DateTimeField(null=True, blank=True, verbose_name=_('Date de mise à jour du mot de passe'))
    first_login = models.BooleanField(default=True, verbose_name=_('Première connexion'))
    first_login_date = models.DateTimeField(null=True, blank=True, verbose_name=_('Date de première connexion'))
    
    password_changed = models.BooleanField(default=False, verbose_name=_('Mot de passe modifié'))
    reset_code = models.CharField(max_length=6, blank=True, null=True, verbose_name=_('Code de réinitialisation'))
    
    # Ajout des related_name pour éviter les conflits
    groups = models.ManyToManyField(Group, related_name='customuser_groups', blank=True, verbose_name=_('Groupes'))
    user_permissions = models.ManyToManyField(Permission, related_name='customuser_permissions', blank=True, verbose_name=_('Permissions utilisateur'))

    class Meta:
        verbose_name = _('Utilisateur personnalisé')
        verbose_name_plural = _('Utilisateurs personnalisés')
        ordering = ['-date_joined']

    def save(self, *args, **kwargs):
        self.clean()
        is_new = self._state.adding  # Vérifie si l'utilisateur est nouveau

        # Définir le rôle en fonction de is_superuser
        if self.is_superuser:
            self.role = 'admin'
        elif not self.role:
            self.role = 'student'

        with transaction.atomic():
            super().save(*args, **kwargs)

            if is_new or self.role:
                group, _ = Group.objects.get_or_create(name=self.role.capitalize())
                self.groups.add(group)

        # Mise à jour des champs liés au mot de passe
        if self.password_changed:
            self.password_updated_at = timezone.now()
            self.password_changed = False
            self.first_login = False
            # Utilise update_fields pour éviter une boucle infinie
            super().save(update_fields=['password_updated_at', 'password_changed', 'first_login'])

    def needs_password_change(self):
        """Vérifie si l'utilisateur doit changer son mot de passe."""
        if self.first_login or self.password_updated_at is None:
            return True
        days_since_last_update = (timezone.now() - self.password_updated_at).days
        return days_since_last_update >= 90

    def mark_password_as_changed(self):
        """Marquer le mot de passe comme changé et mettre à jour la date."""
        self.password_changed = True
        self.password_updated_at = timezone.now()
        self.first_login = False

    def has_role(self, role):
        if not self.is_authenticated:
            return False
        return self.role == role

    @property
    def is_student(self):
        return self.has_role('student')

    @property
    def is_teacher(self):
        return self.has_role('teacher')

    @property
    def is_parent(self):
        return self.has_role('parent')

    @property
    def is_admin(self):
        return self.has_role('admin')

class AdminType(models.Model):
    ADMIN_TYPE_CHOICES = (
        ('admin_general', _('Administrateur Général')),
        ('admin_exams', _('Administrateur des Examens')),
    )
    name = models.CharField(max_length=50, choices=ADMIN_TYPE_CHOICES, default='admin_general', verbose_name=_('Type d’administrateur'))
    description = models.TextField(blank=True, verbose_name=_('Description'))

    def __str__(self):
        return self.get_name_display()

class AdminProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, verbose_name=_('Utilisateur'))
    # managed_departments = models.TextField(blank=True, verbose_name=_('Départements gérés'))
    admin_type = models.ForeignKey(AdminType, on_delete=models.SET_NULL, null=True, related_name='admins', verbose_name=_('Type d’admin'))

    def __str__(self):
        return f'{self.user.username} - {self.admin_type.name}'
    
class TeacherProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, verbose_name=_('Utilisateur'))
    grade = models.CharField(max_length=50, blank=True, verbose_name=_('Grade'))
    subjects = models.ManyToManyField(Subject, related_name='teachers', verbose_name=_("Matières enseignées"))
    
    def teaches_subject(self, subject):
        """vérifier si un enseignant enseigne un sujet spécifique."""
        return subject in self.subjects.all()

    def get_subjects(self):
        """Retourne les matières que l'enseignant enseigne"""
        return self.subjects.all()

    def __str__(self):
        return f'{self.user.username} - {self.grade}'

    class Meta:
        verbose_name = _('Profil Enseignant')
        ordering = ['user__last_name']
        
class StudentProfile(models.Model):
    ENROLLMENT_CHOICES = [
        ('active', _('Actif')),
        ('graduated', _('Diplômé')),
        ('withdrawn', _('Désinscrit')),
    ]
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, verbose_name=_('Utilisateur'))
    student_id = models.CharField(max_length=20, null=True, blank=True, db_index=True, verbose_name=_('ID étudiant'))
    enrollment_status = models.CharField(max_length=20, choices=ENROLLMENT_CHOICES, default='active', verbose_name=_('Statut d’inscription'))
    major = models.ForeignKey(DepartmentLevel, on_delete=models.CASCADE, related_name='students', verbose_name=_('Fillière d’étude'))
    is_class_representative = models.BooleanField(default=False, verbose_name=_('Représentant de classe'))

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} - {self.major}"

    def save(self, *args, **kwargs):
        # Limiter à 3 responsables par niveau
        if self.is_class_representative:
            num_representatives = StudentProfile.objects.filter(
                major=self.major, is_class_representative=True
            ).exclude(pk=self.pk).count()
            if num_representatives >= 3:
                raise ValidationError(
                    _(f"Il ne peut pas y avoir plus de trois représentants dans le niveau {self.major}. Actuellement : {num_representatives}.")
            )
        super().save(*args, **kwargs)

    def get_enrollment_status(self):
        """Retourne le statut d'inscription de l'étudiant"""
        return self.get_enrollment_status_display()

    class Meta:
        verbose_name = _('Profil Étudiant')
        ordering = ['user__last_name']

class ParentProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, verbose_name=_('Utilisateur'))
    children = models.ManyToManyField(StudentProfile, related_name='parents', verbose_name=_('Enfants'))

    def __str__(self):
        return f'Parent: {self.user.username} - {self.children.count()} enfant(s)'
    
    def get_children_names(self):
        return ", ".join([child.__str__() for child in self.children.all()])

    class Meta:
        verbose_name = _('Profil Parent')