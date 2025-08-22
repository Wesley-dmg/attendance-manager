import random
from datetime import timedelta
import re

from django.contrib.auth.models import AbstractUser, Group, Permission
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db import models, transaction
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator

phone_number_validator = RegexValidator(
    regex=r"^(\+229\d{8}|\d{8})$",
    message="Numéro invalide. Format attendu : +22997011234 ou 97011234",
)


class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ("student", _("Étudiant")),
        ("teacher", _("Enseignant")),
        ("parent", _("Parent")),
        ("admin", _("Administrateur")),
    )
    GENDER_CHOICES = [
        ("male", _("Masculin")),
        ("female", _("Féminin")),
        ("other", _("Autre")),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, verbose_name=_("Rôle"))
    phone_number = models.CharField(
        max_length=15,
        blank=True,
        unique=True,
        validators=[phone_number_validator],
        verbose_name=_("Numéro de téléphone"),
    )
    date_of_birth = models.DateField(
        null=True, blank=True, verbose_name=_("Date de naissance")
    )
    address = models.CharField(max_length=255, blank=True, verbose_name=_("Adresse"))
    profile_picture = models.ImageField(
        upload_to="profile_pictures/",
        null=True,
        blank=True,
        db_index=True,
        verbose_name=_("Photo de profil"),
    )
    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES,
        null=True,
        blank=True,
        verbose_name=_("Genre"),
    )

    password_updated_at = models.DateTimeField(
        null=True, blank=True, verbose_name=_("Date de mise à jour du mot de passe")
    )
    first_login = models.BooleanField(
        default=True, verbose_name=_("Première connexion")
    )
    first_login_date = models.DateTimeField(
        null=True, blank=True, verbose_name=_("Date de première connexion")
    )
    password_changed = models.BooleanField(
        default=False, verbose_name=_("Mot de passe modifié")
    )
    reset_code = models.CharField(
        max_length=6, blank=True, null=True, verbose_name=_("Code de réinitialisation")
    )
    reset_code_expiry = models.DateTimeField(
        blank=True, null=True, verbose_name=_("Expiration du code")
    )
    groups = models.ManyToManyField(
        Group, related_name="customuser_groups", blank=True, verbose_name=_("Groupes")
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name="customuser_permissions",
        blank=True,
        verbose_name=_("Permissions utilisateur"),
    )

    class Meta:
        verbose_name = _("Utilisateur personnalisé")
        verbose_name_plural = _("Utilisateurs personnalisés")
        ordering = ["-date_joined"]

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    def clean(self):
        super().clean()

        if self.phone_number:
            # Supprimer les espaces et normaliser
            phone = self.phone_number.replace(" ", "")

            # Si déjà format international, on garde
            if phone.startswith("+229") and len(phone) == 12:
                self.phone_number = phone

            # Si format local (8 chiffres), on ajoute +229
            elif re.match(r"^\d{8}$", phone):
                self.phone_number = f"+229{phone}"

            else:
                raise ValidationError(
                    {
                        "phone_number": "Le numéro doit contenir 8 chiffres avec ou sans préfixe +229."
                    }
                )

    def save(self, *args, **kwargs):
        self.clean()
        is_new = self._state.adding

        # Forcer le rôle "admin" si superutilisateur
        if self.is_superuser:
            self.role = "admin"
        elif not self.role:
            self.role = "student"

        # Gestion de la date de changement de mot de passe et première connexion
        if self.password_changed:
            self.password_updated_at = timezone.now()
            self.password_changed = False
            self.first_login = False

        with transaction.atomic():
            # Sauvegarde unique
            super().save(*args, **kwargs)

            # Ajout automatique au groupe selon le rôle
            if is_new:
                group, _ = Group.objects.get_or_create(name=self.role.capitalize())
                self.groups.add(group)

    def has_role(self, role):
        return self.is_authenticated and self.role == role

    @property
    def is_student(self):
        return self.has_role("student")

    @property
    def is_teacher(self):
        return self.has_role("teacher")

    @property
    def is_parent(self):
        return self.has_role("parent")

    @property
    def is_admin(self):
        return self.has_role("admin")

    @property
    def whatsapp_number(self):
        """
        Retourne le numéro formaté pour WhatsApp, par défaut en ajoutant +229 si nécessaire.
        """
        phone = self.phone_number.strip().replace(" ", "")
        if phone.startswith("+229"):
            return f"whatsapp:{phone}"
        elif phone.startswith("229"):
            return f"whatsapp:+{phone}"
        else:
            return f"whatsapp:+229{phone}"

    def anonymize(self):
        self.first_name = "Anonyme"
        self.last_name = ""
        self.email = None
        self.phone_number = None
        self.address = ""
        self.profile_picture = None
        self.save()


class AdminProfile(models.Model):
    user = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, verbose_name=_("Utilisateur"), unique=True
    )

    def __str__(self):
        return f"Administrateur: {self.user.get_full_name()}"


class TeacherProfile(models.Model):
    user = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, verbose_name=_("Utilisateur")
    )
    grade = models.CharField(max_length=50, blank=True, verbose_name=_("Grade"))
    subjects = models.ManyToManyField(
        "subjects.Subject",
        related_name="teachers",
        verbose_name=_("Matières enseignées"),
    )

    # Champs OTP déplacés ici
    otp_code = models.CharField(
        max_length=6, blank=True, null=True, verbose_name=_("Code OTP")
    )
    otp_code_expiry = models.DateTimeField(
        blank=True, null=True, verbose_name=_("Expiration OTP")
    )

    def __str__(self):
        return f"Enseignant: {self.user.get_full_name()}"

    def generate_otp_code(self, length=6, expire_minutes=5):
        if (
            self.otp_code
            and self.otp_code_expiry
            and timezone.now() < self.otp_code_expiry
        ):
            raise ValidationError(_("Un code OTP est déjà actif. Veuillez attendre."))

        self.otp_code = f"{random.randint(0, 999999):06d}"
        self.otp_code_expiry = timezone.now() + timedelta(minutes=expire_minutes)
        self.save(update_fields=["otp_code", "otp_code_expiry"])

    def is_otp_valid(self, code):
        return (
            self.otp_code == code
            and self.otp_code_expiry
            and timezone.now() <= self.otp_code_expiry
        )

    def teaches_subject(self, subject):
        return subject in self.subjects.all()

    def teaches_subject(self, subject):
        return subject in self.subjects.all()

    def get_subjects(self):
        return self.subjects.all()

    class Meta:
        verbose_name = _("Profil Enseignant")
        ordering = ["user__last_name"]


class StudentProfile(models.Model):
    ENROLLMENT_CHOICES = [
        ("active", _("Actif")),
        ("graduated", _("Diplômé")),
        ("withdrawn", _("Désinscrit")),
    ]

    user = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, verbose_name=_("Utilisateur")
    )
    student_id = models.CharField(
        max_length=20, null=True, blank=True, unique=True, verbose_name=_("ID étudiant")
    )
    enrollment_status = models.CharField(
        max_length=20,
        choices=ENROLLMENT_CHOICES,
        default="active",
        verbose_name=_("Statut d’inscription"),
    )
    major = models.ForeignKey(
        "courses.DepartmentLevel",
        on_delete=models.CASCADE,
        related_name="students",
        verbose_name=_("Filière d’étude"),
        null=True,
        blank=True,
    )

    archived = models.BooleanField(default=False, verbose_name=_("Archivé"))

    archived_at = models.DateTimeField(
        blank=True, null=True, verbose_name="Date d’archivage"
    )

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.major or 'Non assigné'}"

    def get_enrollment_status(self):
        return self.get_enrollment_status_display()

    class Meta:
        verbose_name = _("Profil Étudiant")
        ordering = ["user__last_name"]


class StudentArchiveHistory(models.Model):
    student = models.ForeignKey(
        StudentProfile, on_delete=models.CASCADE, related_name="archive_history"
    )
    action = models.CharField(
        max_length=10, choices=[("archived", "Archivé"), ("unarchived", "Désarchivé")]
    )
    performed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student} - {self.action} - {self.performed_at.date()}"


class ParentProfile(models.Model):
    user = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, verbose_name=_("Utilisateur")
    )
    children = models.ManyToManyField(
        StudentProfile, related_name="parents", verbose_name=_("Enfants")
    )

    RELATION_CHOICES = [
        ("father", "Père"),
        ("mother", "Mère"),
        ("guardian", "Tuteur"),
    ]
    relation = models.CharField(
        max_length=10,
        choices=RELATION_CHOICES,
        default="guardian",
        verbose_name=_("Lien avec l’enfant"),
    )

    class Meta:
        verbose_name = _("Profil Parent")

    def __str__(self):
        return f"Parent: {self.user.username} - {self.children.count()} enfant(s)"

    def get_children_names(self):
        return ", ".join([str(child) for child in self.children.all()])
