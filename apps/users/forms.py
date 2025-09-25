import string
import random

from django.core.cache import cache
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

from django import forms
from django.contrib.auth.forms import (
    UserCreationForm,
    AuthenticationForm,
    PasswordChangeForm,
    PasswordResetForm,
    SetPasswordForm,
    UsernameField,
)
from django_select2.forms import Select2MultipleWidget

from django.db.models import Q
from django.utils.text import slugify
from phonenumber_field.formfields import PhoneNumberField as PhoneNumberFormField

from apps.courses.models import DepartmentLevel
from apps.subjects.models import Subject
from apps.users.models import (
    AdminProfile,
    CustomUser,
    ParentProfile,
    Role,
    StudentProfile,
    TeacherProfile,
)


# Formulaire d'inscription pour les administrateurs uniquement
class CustomUserCreationForm(UserCreationForm):
    password1 = forms.CharField(
        label=_("Mot de passe"),
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Mot de passe"}
        ),
        help_text=_("Votre mot de passe doit contenir au moins 8 caractères."),
    )
    password2 = forms.CharField(
        label=_("Confirmez Mot de passe"),
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Confirmez Mot de passe"}
        ),
    )

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError(_("Cet email est déjà utilisé."))
        return email

    class Meta:
        model = CustomUser
        fields = ["username", "email", "phone_number"]
        widgets = {
            "username": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Nom d'utilisateur"}
            ),
            "email": forms.EmailInput(
                attrs={"class": "form-control", "placeholder": "Email"}
            ),
            "phone_number": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Numéro de téléphone"}
            ),
        }

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(_("Les mots de passe ne correspondent pas."))

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = "admin"
        if commit:
            user.save()
        return user


# Formulaire de connexion
class CustomLoginForm(AuthenticationForm):
    username = UsernameField(
        label=_("Nom d'utilisateur"),
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Nom d'utilisateur"}
        ),
    )
    password = forms.CharField(
        label=_("Votre mot de passe"),
        strip=False,
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Mot de passe"}
        ),
    )

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if not CustomUser.objects.filter(username=username).exists():
            raise forms.ValidationError(_("Nom d'utilisateur introuvable."))
        return username

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get("username")

        # Vérifiez que l'utilisateur existe avant de le récupérer
        user = CustomUser.objects.filter(username=username).first()
        if user is None:
            # Si l'utilisateur n'existe pas, ne retournez pas simplement cleaned_data
            raise forms.ValidationError(
                _("Nom d'utilisateur ou mot de passe incorrect.")
            )

        return cleaned_data


# Formulaire de changement de mot de passe
class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        label=_("Ancien mot de passe"),
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Ancien mot de passe"}
        ),
    )
    new_password1 = forms.CharField(
        label=_("Nouveau mot de passe"),
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Nouveau mot de passe"}
        ),
    )
    new_password2 = forms.CharField(
        label=_("Confirmer le nouveau mot de passe"),
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Confirmer le nouveau mot de passe",
            }
        ),
    )

    def save(self, commit=True):
        user = super().save(commit=commit)
        user.mark_password_as_changed()  # Marque le mot de passe comme changé
        if commit:
            user.save()
        return user


# Formulaire de demande de réinitialisation du mot de passe
class CustomPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={"class": "form-control", "placeholder": "Email"}
        ),
        label=_("Email"),
    )

    def clean_email(self):
        email = self.cleaned_data["email"]
        cache_key = f"password_reset_attempts_{email}"
        attempts = cache.get(cache_key, 0)

        if attempts >= 5:
            raise forms.ValidationError(_("Ça suffit ! Réessayez demain."))

        cache.set(cache_key, attempts + 1, 86400)  # Durée de 24 heures
        return email

    class Meta:
        model = CustomUser
        fields = ["email"]


# Formulaire de réinitialisation du mot de passe
class CustomSetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(
        max_length=50,
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Nouveau mot de passe"}
        ),
        label=_("Nouveau mot de passe"),
    )
    new_password2 = forms.CharField(
        max_length=50,
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Confirmer le nouveau mot de passe",
            }
        ),
        label=_("Confirmer le nouveau mot de passe"),
    )


# Fonction pour générer un mot de passe sécurisé
def generate_secure_password(length=12):
    while True:
        password = "".join(
            random.choice(
                string.ascii_uppercase
                + string.ascii_lowercase
                + string.digits
                + "!@#$%^&*()-_=+"
            )
            for _ in range(length)
        )
        if (
            any(c.islower() for c in password)
            and any(c.isupper() for c in password)
            and any(c.isdigit() for c in password)
            and any(c in "!@#$%^&*()-_=+" for c in password)
        ):
            break
    return password


class PasswordResetCodeForm(forms.Form):
    """
    Formulaire pour que l'utilisateur entre le code de réinitialisation
    qu'il a reçu par email. Ce code est un champ requis de 6 caractères.
    """

    code = forms.CharField(
        label="Code de réinitialisation",
        max_length=6,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Entrez votre code de réinitialisation",
            }
        ),
    )


# ======================
# Formulaire de base
# ======================
class BaseUserForm(forms.ModelForm):
    first_name = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Prénom"})
    )
    last_name = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Nom"})
    )
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(
            attrs={"class": "form-control", "placeholder": "Email"}
        ),
        label="Email",
    )
    date_of_birth = forms.DateField(
        widget=forms.DateInput(
            attrs={
                "class": "form-control",
                "type": "date",
                "placeholder": "AAAA-MM-JJ",
            },
            format="%Y-%m-%d",
        ),
        required=False,
    )
    gender = forms.ChoiceField(
        choices=CustomUser.GENDER_CHOICES,
        widget=forms.Select(attrs={"class": "form-control"}),
        required=False,
    )
    phone_number = PhoneNumberFormField(
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "+22912345678",  # placeholder international
                "inputmode": "numeric",  # clavier numérique mobile
            }
        ),
        label="Téléphone",
    )

    class Meta:
        model = CustomUser
        fields = [
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "date_of_birth",
            "gender",
        ]

    def clean_phone_number(self):
        phone = self.cleaned_data.get("phone_number")
        if (
            phone
            and CustomUser.objects.exclude(pk=self.instance.pk)
            .filter(phone_number=phone)
            .exists()
        ):
            raise forms.ValidationError(_("Ce numéro de téléphone est déjà utilisé."))
        return phone


# ======================
# Admin
# ======================
class AdminForm(BaseUserForm):
    role = forms.ModelMultipleChoiceField(
        queryset=Role.objects.all(),
        widget=Select2MultipleWidget(attrs={"class": "form-control select2"}),
        required=True,
        label="Rôles",
    )

    class Meta(BaseUserForm.Meta):
        fields = BaseUserForm.Meta.fields + ["role"]

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            # Sauvegarder les rôles
            user.role.set(self.cleaned_data["role"])

            # Création ou mise à jour du profil admin
            AdminProfile.objects.get_or_create(user=user)

            # Si admin a aussi "teacher" → créer ou maj TeacherProfile
            if user.has_role("teacher"):
                TeacherProfile.objects.get_or_create(user=user)
        return user


class AdminUpdateForm(BaseUserForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            admin_role, _ = Role.objects.get_or_create(name="admin")
            user.role.add(admin_role)
            AdminProfile.objects.get_or_create(user=user)
        return user


# ======================
# Teacher
# ======================
class TeacherForm(BaseUserForm):
    subjects = forms.ModelMultipleChoiceField(
        queryset=Subject.objects.all(),
        widget=Select2MultipleWidget(attrs={"class": "form-control select2"}),
        required=True,
    )

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            teacher_role, _ = Role.objects.get_or_create(name="teacher")
            user.role.add(teacher_role)
            teacher_profile, _ = TeacherProfile.objects.get_or_create(user=user)
            teacher_profile.subjects.set(self.cleaned_data["subjects"])
            teacher_profile.save()
        return user


class TeacherUpdateForm(BaseUserForm):
    subjects = forms.ModelMultipleChoiceField(
        queryset=Subject.objects.all(), widget=Select2MultipleWidget, required=True
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and hasattr(self.instance, "teacherprofile"):
            self.fields["subjects"].initial = (
                self.instance.teacherprofile.subjects.all()
            )

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            teacher_role, _ = Role.objects.get_or_create(name="teacher")
            user.role.add(teacher_role)
            teacher_profile, _ = TeacherProfile.objects.get_or_create(user=user)
            teacher_profile.subjects.set(self.cleaned_data["subjects"])
            teacher_profile.save()
        return user


# ======================
# Student
# ======================
class StudentForm(BaseUserForm):
    major = forms.ModelChoiceField(
        queryset=DepartmentLevel.objects.all(),
        widget=forms.Select(attrs={"class": "form-control select2"}),
        required=True,
        label="Filière",
    )

    def save(self, commit=True):
        user = super().save(commit=False)
        student_role, _ = Role.objects.get_or_create(name="student")
        if commit:
            user.save()
            user.role.set([student_role])  # Remplace tous les autres rôles
            student_profile, _ = StudentProfile.objects.get_or_create(user=user)
            student_profile.major = self.cleaned_data["major"]
            student_profile.save()
        return user


class StudentUpdateForm(BaseUserForm):
    major = forms.ModelChoiceField(
        queryset=DepartmentLevel.objects.all(),
        widget=forms.Select(attrs={"class": "form-control select2"}),
        required=True,
        label="Filière",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and hasattr(self.instance, "studentprofile"):
            self.fields["major"].initial = self.instance.studentprofile.major

    def save(self, commit=True):
        user = super().save(commit=False)
        student_role, _ = Role.objects.get_or_create(name="student")
        if commit:
            user.save()
            user.role.set([student_role])
            student_profile, _ = StudentProfile.objects.get_or_create(user=user)
            student_profile.major = self.cleaned_data["major"]
            student_profile.save()
        return user


# ======================
# Parent
# ======================
class ParentForm(BaseUserForm):
    children = forms.ModelMultipleChoiceField(
        queryset=StudentProfile.objects.all(),
        widget=forms.SelectMultiple(attrs={"class": "form-control select2"}),
        required=True,
        label="Enfants",
    )

    RELATION_CHOICES = [
        ("father", "Père"),
        ("mother", "Mère"),
        ("guardian", "Tuteur"),
    ]
    relation = forms.ChoiceField(
        choices=RELATION_CHOICES,
        widget=forms.Select(attrs={"class": "form-control"}),
        label="Lien avec l’enfant",
        required=True,
    )

    def __init__(self, *args, **kwargs):
        self.student_instance = kwargs.pop("student_instance", None)
        self.allow_existing_phone = kwargs.pop("allow_existing_phone", False)
        super().__init__(*args, **kwargs)

        if self.student_instance:
            # Création à partir d’un élève → champ enfants caché et forcé
            self.fields["children"] = forms.ModelMultipleChoiceField(
                queryset=StudentProfile.objects.filter(pk=self.student_instance.pk),
                widget=forms.MultipleHiddenInput(),
                initial=[self.student_instance],
                required=True,
                label="Enfants",
            )

    def save(self, commit=True):
        user = super().save(commit=False)

        # Génération automatique d’un username unique
        base_username = slugify(user.first_name) or "user"
        username = base_username
        User = get_user_model()
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{random.randint(10, 99)}"
        user.username = username

        if commit:
            user.save()

            # Ajout du rôle parent
            parent_role, _ = Role.objects.get_or_create(name="parent")
            user.role.add(parent_role)

            parent_profile, _ = ParentProfile.objects.get_or_create(user=user)

            # Associer l’enfant automatiquement
            if self.student_instance:
                print(">> Association automatique de l'élève au parent")
                print("   Élève ID:", self.student_instance.pk)
                parent_profile.children.add(self.student_instance)
            else:
                print(">> Association via champ children (sélection manuelle)")
                parent_profile.children.set(self.cleaned_data["children"])

            parent_profile.relation = self.cleaned_data["relation"]
            parent_profile.save()
            print(">> ParentProfile enregistré :", parent_profile.pk)
            print(
                ">> Enfants associés :",
                list(parent_profile.children.values_list("pk", flat=True)),
            )
        return user


class ParentUpdateForm(BaseUserForm):
    children = forms.ModelMultipleChoiceField(
        queryset=StudentProfile.objects.all(),
        widget=forms.SelectMultiple(attrs={"class": "form-control select2"}),
        required=True,
        label="Enfants",
    )
    RELATION_CHOICES = [
        ("father", "Père"),
        ("mother", "Mère"),
        ("guardian", "Tuteur"),
    ]
    relation = forms.ChoiceField(
        choices=RELATION_CHOICES,
        widget=forms.Select(attrs={"class": "form-control"}),
        label="Lien avec l’enfant",
        required=True,
    )

    def __init__(self, *args, **kwargs):
        self.student_instance = kwargs.pop("student_instance", None)
        super().__init__(*args, **kwargs)
        if self.instance and hasattr(self.instance, "parentprofile"):
            profile = self.instance.parentprofile
            self.fields["children"].initial = profile.children.all()
            self.fields["relation"].initial = profile.relation
        if self.student_instance:
            self.fields["children"].initial = list(self.fields["children"].initial) + [
                self.student_instance
            ]
            self.fields["children"].queryset = StudentProfile.objects.filter(
                Q(pk__in=[c.pk for c in self.fields["children"].initial])
                | Q(pk=self.student_instance.pk)
            )

    def save(self, commit=True):
        user = super().save(commit=False)
        parent_role, _ = Role.objects.get_or_create(name="parent")
        if commit:
            user.save()
            user.role.set([parent_role])
            parent_profile, _ = ParentProfile.objects.get_or_create(user=user)
            parent_profile.children.set(self.cleaned_data["children"])
            parent_profile.relation = self.cleaned_data["relation"]
            parent_profile.save()
        return user


class UserUpdateForm(forms.ModelForm):
    phone_number = PhoneNumberFormField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Ex: +229 91234567",
                "type": "tel",
                "inputmode": "numeric",
            }
        ),
        label="Numéro de téléphone",
    )

    class Meta:
        model = CustomUser
        fields = [
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "address",
            "profile_picture",
        ]
        widgets = {
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "address": forms.TextInput(attrs={"class": "form-control"}),
        }
