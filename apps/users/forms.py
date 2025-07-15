from django.utils.translation import gettext_lazy as _
from django.contrib.auth.forms import (UserCreationForm, AuthenticationForm, PasswordChangeForm, PasswordResetForm, SetPasswordForm, UsernameField,UserChangeForm)
from apps.courses.models import DepartmentLevel
from apps.subjects.models import Subject
from django_select2.forms import Select2MultipleWidget
from django.core.cache import cache
from django import forms
from .models import *
import random
import string

# Formulaire d'inscription pour les administrateurs uniquement
class CustomUserCreationForm(UserCreationForm):
    password1 = forms.CharField(
        label=_("Mot de passe"),
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Mot de passe'}),
        help_text=_("Votre mot de passe doit contenir au moins 8 caractères."),
    )
    password2 = forms.CharField(
        label=_("Confirmez Mot de passe"),
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirmez Mot de passe'}),
    )

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError(_("Cet email est déjà utilisé."))
        return email

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'phone_number']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom d\'utilisateur'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Numéro de téléphone'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(_("Les mots de passe ne correspondent pas."))

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'admin'  # Rôle générique pour tous les types d'admin
        if commit:
            user.save()
            
            # Récupération ou création de l'AdminType
            # admin_type_name = self.cleaned_data['admin_type']
            # admin_type, created = AdminType.objects.get_or_create(name=admin_type_name)
            
            # Crée le profil Admin avec le type spécifié
            AdminProfile.objects.create(user=user
                                        # , admin_type=admin_type
                                        )

        return user

# Formulaire de connexion
class CustomLoginForm(AuthenticationForm):
    username = UsernameField(
        label=_("Nom d'utilisateur"), 
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Nom d'utilisateur"})
        )
    password = forms.CharField(
        label=_("Votre mot de passe"),
        strip=False,
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Mot de passe"}),
    )

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not CustomUser.objects.filter(username=username).exists():
            raise forms.ValidationError(_("Nom d'utilisateur introuvable."))
        return username

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        
        # Vérifiez que l'utilisateur existe avant de le récupérer
        user = CustomUser.objects.filter(username=username).first()
        if user is None:
            # Si l'utilisateur n'existe pas, ne retournez pas simplement cleaned_data
            raise forms.ValidationError(_("Nom d'utilisateur ou mot de passe incorrect."))
        
        return cleaned_data

# Formulaire de changement de mot de passe
class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        label=_("Ancien mot de passe"),
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Ancien mot de passe'}),
    )
    new_password1 = forms.CharField(
        label=_("Nouveau mot de passe"),
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Nouveau mot de passe'}),
    )
    new_password2 = forms.CharField(
        label=_("Confirmer le nouveau mot de passe"),
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirmer le nouveau mot de passe'}),
    )

    def save(self, commit=True):
        user = super().save(commit=commit)
        user.mark_password_as_changed()  # Marque le mot de passe comme changé
        if commit:
            user.save()
        return user
    
# Formulaire de demande de réinitialisation du mot de passe
class CustomPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Email'
    }), label=_("Email"))

    def clean_email(self):
        email = self.cleaned_data['email']
        cache_key = f'password_reset_attempts_{email}'
        attempts = cache.get(cache_key, 0)

        if attempts >= 5:
            raise forms.ValidationError(
                _("Ça suffit ! Réessayez demain.")
            )

        cache.set(cache_key, attempts + 1, 86400)  # Durée de 24 heures
        return email

    class Meta:
        model = CustomUser
        fields = ['email']

# Formulaire de réinitialisation du mot de passe
class CustomSetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(max_length=50, widget=forms.PasswordInput(attrs={
        'class': 'form-control', 'placeholder': 'Nouveau mot de passe'
    }), label=_("Nouveau mot de passe"))
    new_password2 = forms.CharField(max_length=50, widget=forms.PasswordInput(attrs={
        'class': 'form-control', 'placeholder': 'Confirmer le nouveau mot de passe'
    }), label=_("Confirmer le nouveau mot de passe"))

# Fonction pour générer un mot de passe sécurisé
def generate_secure_password(length=12):
    while True:
        password = ''.join(random.choice(
            string.ascii_uppercase + string.ascii_lowercase + string.digits + "!@#$%^&*()-_=+"
        ) for _ in range(length))
        if (any(c.islower() for c in password) and
            any(c.isupper() for c in password) and
            any(c.isdigit() for c in password) and
            any(c in "!@#$%^&*()-_=+" for c in password)):
            break
    return password

class PasswordResetCodeForm(forms.Form):
    """
    Formulaire pour que l'utilisateur entre le code de réinitialisation
    qu'il a reçu par email. Ce code est un champ requis de 6 caractères.
    """
    code = forms.CharField(
        label='Code de réinitialisation',
        max_length=6,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Entrez votre code de réinitialisation'
        })
    )

# Formulaire de base avec les champs partagés
class BaseUserForm(forms.ModelForm):
    first_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Prénom'}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom'}))
    email = forms.EmailField(required=False,widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),label="Email")
    date_of_birth = forms.DateField(
    widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'placeholder': 'AAAA-MM-JJ'}, format='%Y-%m-%d'),required=False)
    gender = forms.ChoiceField(choices=CustomUser.GENDER_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}), required=False)
    phone_number = forms.CharField( required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Téléphone'}), label="Téléphone")
    
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'date_of_birth', 'gender']
    
    def clean_phone_number(self):
        phone = self.cleaned_data['phone_number']
        qs = CustomUser.objects.filter(phone_number=phone)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Ce numéro de téléphone est déjà utilisé.")
        return phone


# Formulaire pour les administrateurs
class AdminForm(BaseUserForm):
    # admin_type = forms.ModelChoiceField(queryset=AdminType.objects.all(), widget=forms.Select(attrs={'class': 'form-control'}), required=True)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'admin'
        if commit:
            user.save()
            
            # Vérifier si un AdminProfile existe déjà pour cet utilisateur
            if not hasattr(user, 'adminprofile'):
                AdminProfile.objects.create(user=user
                                            # , admin_type=self.cleaned_data['admin_type']
                                            )
            else:
                # Gérer le cas où le profil existe déjà, par exemple, mettre à jour les informations
                # user.adminprofile.admin_type = self.cleaned_data['admin_type']
                user.adminprofile.save()
        return user

# Formulaire pour les enseignants
class TeacherForm(BaseUserForm):
    subjects = forms.ModelMultipleChoiceField(queryset=Subject.objects.all(), widget=Select2MultipleWidget(attrs={'class': 'form-control select2'}), required=True)
    
    
    # department_levels = forms.ModelMultipleChoiceField(queryset=DepartmentLevel.objects.all(), widget=Select2MultipleWidget, required=False)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'teacher'
        if commit:
            user.save()
            teacher_profile, created = TeacherProfile.objects.get_or_create(user=user)
            teacher_profile.subjects.set(self.cleaned_data['subjects'])
                
        return user
    
    def clean_phone_number(self):
        phone = self.cleaned_data['phone_number']
        if CustomUser.objects.filter(phone_number=phone).exists():
            raise forms.ValidationError("Ce numéro de téléphone est déjà utilisé.")
        return phone

# Formulaire pour les étudiants
class StudentForm(BaseUserForm):
    major = forms.ModelChoiceField(queryset=DepartmentLevel.objects.all(), widget=forms.Select(attrs={'class': 'form-control'}), required=True)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'student'
        if commit:
            user.save()
            student_profile, created = StudentProfile.objects.get_or_create(
                user=user, 
                defaults={'major': self.cleaned_data['major']}
            )
            
            # Si le profil existait déjà, on met à jour le champ `major` avec la valeur actuelle
            if not created:
                student_profile.major = self.cleaned_data['major']
                student_profile.save()

        return user

# Formulaire pour les parents
class ParentForm(BaseUserForm):
    children = forms.ModelMultipleChoiceField(queryset=StudentProfile.objects.all(),widget=Select2MultipleWidget, required=True)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'parent'
        if commit:
            user.save()
            parent_profile, created = ParentProfile.objects.get_or_create(user=user)
            if not created:
                # Mise à jour des enfants si le profil existait déjà
                parent_profile.children.set(self.cleaned_data['children'])
            else:
                parent_profile.children.add(*self.cleaned_data['children'])
            parent_profile.save()
        return user
    
class AdminUpdateForm(BaseUserForm):
    # admin_type = forms.ModelChoiceField(queryset=AdminType.objects.all(), widget=forms.Select(attrs={'class': 'form-control'}), required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # if self.instance and hasattr(self.instance, 'adminprofile'):
        #     self.fields['admin_type'].initial = self.instance.adminprofile.admin_type

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'admin'
        if commit:
            user.save()
            admin_profile, created = AdminProfile.objects.get_or_create(user=user)
            # admin_profile.admin_type = self.cleaned_data['admin_type']
            admin_profile.save()
        return user

class TeacherUpdateForm(BaseUserForm):
    subjects = forms.ModelMultipleChoiceField(queryset=Subject.objects.all(), widget=Select2MultipleWidget, required=True)
    

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and hasattr(self.instance, 'teacherprofile'):
            self.fields['subjects'].initial = self.instance.teacherprofile.subjects.all()
            
    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'teacher'
        if commit:
            user.save()
            teacher_profile, created = TeacherProfile.objects.get_or_create(user=user)
            teacher_profile.subjects.set(self.cleaned_data['subjects'])
            
            teacher_profile.save()
        return user
    
    def clean_phone_number(self):
        phone = self.cleaned_data['phone_number']
        qs = CustomUser.objects.filter(phone_number=phone)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Ce numéro de téléphone est déjà utilisé.")
        return phone

class StudentUpdateForm(BaseUserForm):
    major = forms.ModelChoiceField(queryset=DepartmentLevel.objects.all(), widget=forms.Select(attrs={'class': 'form-control'}), required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and hasattr(self.instance, 'studentprofile'):
            self.fields['major'].initial = self.instance.studentprofile.major

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'student'
        if commit:
            user.save()
            student_profile, created = StudentProfile.objects.get_or_create(user=user)
            student_profile.major = self.cleaned_data['major']
            student_profile.save()
        return user
            
class ParentUpdateForm(BaseUserForm):
    children = forms.ModelMultipleChoiceField(queryset=StudentProfile.objects.all(), widget=Select2MultipleWidget, required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and hasattr(self.instance, 'parentprofile'):
            self.fields['children'].initial = self.instance.parentprofile.children.all()

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'parent'
        if commit:
            user.save()
            parent_profile, created = ParentProfile.objects.get_or_create(user=user)
            parent_profile.children.set(self.cleaned_data['children'])
            parent_profile.save()
        return user


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = [
            'first_name', 
            'last_name', 
            'email', 
            'phone_number', 
            'address', 
            'profile_picture'
        ]
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
        }
