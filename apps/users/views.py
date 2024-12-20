from linecache import cache
import random
import string
from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test,login_required
from django.contrib.auth import login, authenticate, update_session_auth_hash
from django.views.generic import ListView, CreateView, UpdateView, DeleteView,FormView
from django.utils.translation import gettext as _
from django.shortcuts import render, redirect
from django.contrib.auth.views import *
from django.core.mail import send_mail 
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils import timezone

from apps.home.utils import send_custom_message
from apps.users.forms import AdminForm, AdminUpdateForm, CustomLoginForm, CustomPasswordChangeForm, CustomPasswordResetForm, CustomSetPasswordForm, CustomUserCreationForm, ParentForm, ParentUpdateForm, PasswordResetCodeForm, StudentForm, StudentUpdateForm, TeacherForm, TeacherUpdateForm
from apps.users.models import AdminProfile, AdminType, CustomUser

from django.views import View

from django.contrib.auth import get_user_model


def generate_password():
    characters = string.ascii_letters + string.digits + "!@#$%^&*()-_=+"
    return ''.join(random.choice(characters) for _ in range(10))

# Vue pour l'inscription
def CustomregisterView(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Ajoute le type d'administrateur
            admin_type = form.cleaned_data.get('admin_type', 'admin_general')
            
            # Vérifie si le profil admin a été créé ou s'il existe déjà
            admin_profile, created = AdminProfile.objects.get_or_create(
                user=user, 
                defaults={'admin_type': AdminType.objects.get(name=admin_type)}
            )
            
            # Vérifie si le profil a été créé
            if created:
                send_custom_message(request, _("Compte administrateur créé avec succès. Vous pouvez maintenant vous connecter."), 'success')
            else:
                send_custom_message(request, _("Ce profil existe déjà."), 'info')
                
            return redirect('utilisateurs:login')
        else:
            send_custom_message(request, _("Erreur lors de l'inscription. Veuillez vérifier les champs."), 'error')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/auth-signup.html', {'form': form})

# Ajoute les redirections pour chaque rôle dans un dictionnaire pour plus de lisibilité
ROLE_REDIRECTS = {
    'admin': 'home:admin_dashboard',
    'teacher': 'home:teacher_dashboard',
    'student': 'home:student_dashboard',
    'parent': 'home:parent_dashboard'
}

# Vue pour la connexion
def CustomLoginView(request):
    if request.method == 'POST':
        form = CustomLoginForm(data=request.POST)
        
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')

            # Authentifie l'utilisateur avec le nom d'utilisateur et le mot de passe
            user = authenticate(request, username=username, password=password)
            if user is not None:
                # Mets à jour la date de première connexion si elle est vide
                if not user.first_login:
                    user.first_login = timezone.now()
                    user.save()

                # Connexion de l'utilisateur et envoi du message de succès
                login(request, user)
                send_custom_message(request, _("Vous êtes maintenant connecté."),'success')

                # Redirection dynamique basée sur le rôle
                return redirect(ROLE_REDIRECTS.get(user.role, 'home:index'))
            
            else:
                send_custom_message(request, _("Nom d'utilisateur ou mot de passe incorrect."),'error')

        else:
            send_custom_message(request, _("Erreur dans le formulaire. Vérifiez vos informations."),'error')
    
    else:
        form = CustomLoginForm()
    
    return render(request, 'accounts/auth-signin.html', {'form': form})

# Vue pour le changement de mot de passe
class CustomPasswordChangeView(PasswordChangeView):
    form_class = CustomPasswordChangeForm
    template_name = 'accounts/auth-change-password.html'
    success_url = reverse_lazy('users:login')

    def form_valid(self, form):
        user = form.save()
        update_session_auth_hash(self.request, user)
        user.mark_password_as_changed()
        send_custom_message(self.request, _("Votre mot de passe a été changé avec succès."), 'success')
        return super().form_valid(form)

# Vue pour la demande de réinitialisation du mot de passe
class CustomPasswordResetView(PasswordResetView):
    form_class = CustomPasswordResetForm
    template_name = 'accounts/auth-reset-password.html'
    success_url = reverse_lazy('users:password_reset_code')

    def form_valid(self, form):
        email = form.cleaned_data['email']
        user = CustomUser.objects.filter(email=email).first()
        
        if not user:
            send_custom_message(self.request, _("Aucun utilisateur trouvé avec cet email."), 'error')
            return self.form_invalid(form)

        # Génération du code de validation à 6 chiffres
        reset_code = ''.join(random.choices('0123456789', k=6))
        
        # Vérification de l'unicité (non nécessaire si c'est un code aléatoire mais peut être ajouté pour la sécurité)
        existing_code_user = CustomUser.objects.filter(reset_code=reset_code).first()
        while existing_code_user:
            reset_code = ''.join(random.choices('0123456789', k=6))
            existing_code_user = CustomUser.objects.filter(reset_code=reset_code).first()

        user.reset_code = reset_code
        user.save()

        # Envoie du code par email
        send_mail(
            'Code de réinitialisation de votre mot de passe',
            f'Votre code de réinitialisation est : {reset_code}',
            'from@example.com',
            [email],
            fail_silently=False,
        )

        send_custom_message(self.request, _("Un code de réinitialisation a été envoyé par email."), 'success')

        # Stocke le code dans le cache avec une expiration
        cache.set(f'reset_code_{user.id}', reset_code, timeout=160)  # 160 secondes = 3 minutes

        return redirect(self.success_url)

# Vue pour réinitialiser le mot de passe
class CustomPasswordResetConfirmView(FormView):
    template_name = 'accounts/auth-password-reset-confirm.html'
    form_class = CustomSetPasswordForm
    success_url = reverse_lazy('users:login')

    def dispatch(self, request, *args, **kwargs):
        """
        Vérifie si l'ID de l'utilisateur est dans la session.
        Si ce n'est pas le cas, redirige vers la demande de réinitialisation.
        """
        self.user_id = request.session.get('reset_user_id')
        if not self.user_id:
            send_custom_message(self.request, _("Session expirée. Veuillez recommencer le processus de réinitialisation."),'error')
            return redirect('users:password_reset')
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        """
        Fournit des arguments au formulaire, y compris l'utilisateur chargé à partir de l'ID en session.
        """
        kwargs = super().get_form_kwargs()
        kwargs['user'] = CustomUser.objects.get(id=self.user_id)  # Charge l'utilisateur en fonction de l'ID en session
        return kwargs

    def form_valid(self, form):
        """
        Enregistre le nouveau mot de passe et nettoie la session.
        """
        form.save()  # Met à jour le mot de passe de l'utilisateur
        send_custom_message(self.request, _("Votre mot de passe a été mis à jour avec succès."),'success')
        del self.request.session['reset_user_id']  # Nettoie la session pour la sécurité
        return super().form_valid(form)

class PasswordResetCodeView(View):
    template_name = 'accounts/password_reset_code.html'
    form_class = PasswordResetCodeForm

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']
            user = CustomUser.objects.filter(reset_code=code).first()
            if user:
                # Code validé - on stocke l'ID de l'utilisateur pour la réinitialisation
                request.session['reset_user_id'] = user.id
                user.reset_code = None  # Supprime le code pour la sécurité
                user.save()
                send_custom_message(self.request, _("Code validé. Vous pouvez maintenant définir un nouveau mot de passe."), 'success')
                return redirect('utilisateurs:password_reset_confirm')
            else:
                send_custom_message(self.request, _("Code de réinitialisation invalide."),'error')
        return render(request, self.template_name, {'form': form})


# Liste 
@method_decorator([login_required, user_passes_test(lambda u: u.is_admin())], name='dispatch')
class AdminListView(ListView):
    model = CustomUser
    template_name = 'users/admin/admins_list.html'
    context_object_name = 'users'
    extra_context = {
        'role': 'admin',
        'create_url': reverse_lazy('users:create_admin'),
        'edit_url': 'users:edit_admin',
        'delete_url': 'users:delete_admin',
    }

    def get_queryset(self):
        return CustomUser.objects.filter(role='admin')

@method_decorator([login_required, user_passes_test(lambda u: u.is_admin())], name='dispatch')
class TeacherListView(ListView):
    model = CustomUser
    template_name = 'users/admin/teachers_list.html'
    context_object_name = 'users'
    extra_context = {
        'role': 'teacher',
        'create_url': reverse_lazy('users:create_teacher'),
        'edit_url': 'users:edit_teacher',
        'delete_url': 'users:delete_teacher',
    }

    def get_queryset(self):
        return CustomUser.objects.filter(role='teacher').select_related('teacherprofile')

@method_decorator([login_required, user_passes_test(lambda u: u.is_admin())], name='dispatch')
class StudentListView(ListView):
    model = CustomUser
    template_name = 'users/admin/students_list.html'
    context_object_name = 'users'
    extra_context = {
        'role': 'student',
        'create_url': reverse_lazy('users:create_student'),
        'edit_url': 'users:edit_student',
        'delete_url': 'users:delete_student',
    }

    def get_queryset(self):
        return CustomUser.objects.filter(role='student')

@method_decorator([login_required, user_passes_test(lambda u: u.is_admin())], name='dispatch')
class ParentListView(ListView):
    model = CustomUser
    template_name = 'users/admin/parents_list.html'
    context_object_name = 'users'
    extra_context = {
        'role': 'parent',
        'create_url': reverse_lazy('users:create_parent'),
        'edit_url': 'users:edit_parent',
        'delete_url': 'users:delete_parent',
    }

    def get_queryset(self):
        return CustomUser.objects.filter(role='parent')

@method_decorator([login_required, user_passes_test(lambda u: u.is_admin())], name='dispatch')
class UserCreateView(CreateView):
    template_name = 'users/admin/user_form.html'
    success_url = reverse_lazy('users:admins_list')

    def form_valid(self, form):
        # Vérification si un utilisateur existe déjà avec cet email ou nom d'utilisateur
        username = form.cleaned_data['email'].split('@')[0]
        email = form.cleaned_data['email']

        User = get_user_model()
        if User.objects.filter(username=username).exists():
            form.add_error('email', "Un utilisateur avec ce nom d'utilisateur existe déjà.")
            return self.form_invalid(form)
        
        if User.objects.filter(email=email).exists():
            form.add_error('email', "Un utilisateur avec cet email existe déjà.")
            return self.form_invalid(form)

        # Générer un nom d'utilisateur et mot de passe
        form.instance.username = form.cleaned_data['email'].split('@')[0]
        password = generate_password()
        form.instance.set_password(password)
        
        # Sauvegarder l'utilisateur et envoyer l'email
        user = form.save()
        send_mail(
            'Bienvenue',
            f'Nom d’utilisateur: {user.username}\nMot de passe: {password}\nLien: {self.request.build_absolute_uri(reverse_lazy("utilisateurs:login"))}',
            'admin@exemple.com',
            [user.email],
            fail_silently=False,
        )
        send_custom_message(self.request, _(f"{user.role.capitalize()} créé avec succès et email envoyé."),'success')
        return super().form_valid(form)

# Vue pour les administrateurs
class AdminCreateView(UserCreateView):
    form_class = AdminForm
    success_url = reverse_lazy('utilisateurs:admins_list')
    extra_context = {'role': 'admin',
                     'title': 'Ajouter Administrateur',
                     'cancel_url': reverse_lazy('utilisateurs:admins_list')}

    def form_invalid(self, form):
        # Message d'erreur si le formulaire est invalide
        send_custom_message(self.request, _("Erreur dans le formulaire. Un profil Administrateur pour cet utilisateur existe déjà."), 'error')
        return super().form_invalid(form)
    
# Vue pour les enseignants
class TeacherCreateView(UserCreateView):
    form_class = TeacherForm
    success_url = reverse_lazy('utilisateurs:teachers_list')
    extra_context = {'role': 'teacher',
                     'title': 'Ajouter Administrateur',
                     'cancel_url': reverse_lazy('utilisateurs:teachers_list')}
    
    def form_invalid(self, form):
        # Message d'erreur si le formulaire est invalide
        send_custom_message(self.request, _("Erreur dans le formulaire. Un profil enseignant pour cet utilisateur existe déjà."), 'error')
        return super().form_invalid(form)

# Vue pour les étudiants
class StudentCreateView(UserCreateView):
    form_class = StudentForm
    success_url = reverse_lazy('utilisateurs:students_list')
    extra_context = {'role': 'student',
                     'title': 'Ajouter Étudiant',
                     'cancel_url': reverse_lazy('utilisateurs:students_list')}

    def form_invalid(self, form):
        # Message d'erreur si le formulaire est invalide
        send_custom_message(self.request, _("Erreur dans le formulaire. Un profil Étudiant pour cet utilisateur existe déjà."), 'error')
        return super().form_invalid(form)

# Vue pour les parents
class ParentCreateView(UserCreateView):
    form_class = ParentForm
    success_url = reverse_lazy('utilisateurs:parents_list')
    extra_context = {'role': 'parent',
                     'title': 'Ajouter Parent',
                     'cancel_url': reverse_lazy('utilisateurs:parents_list')}

    def form_invalid(self, form):
        # Message d'erreur si le formulaire est invalide
        send_custom_message(self.request, _("Erreur dans le formulaire. Un profil Parent pour cet utilisateur existe déjà."), 'error')
        return super().form_invalid(form)

@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(lambda u: u.is_admin()), name='dispatch')
class AdminUpdateView(UpdateView):
    model = CustomUser
    form_class = AdminUpdateForm  # Utilisez AdminUpdateForm au lieu de AdminForm
    template_name = 'users/admin/user_form.html'
    extra_context = {
        'title': 'Modifier Administrateur',
        'cancel_url': reverse_lazy('utilisateurs:admins_list'),
    }

    def get_initial(self):
        initial = super().get_initial()
        # Convertit la date de naissance en format ISO pour être compatible avec le champ date
        if self.object.date_of_birth:
            initial['date_of_birth'] = self.object.date_of_birth.strftime('%Y-%m-%d')
        return initial
    
    def get_success_url(self):
        return self.extra_context['cancel_url']  # Redirige après la mise à jour

@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(lambda u: u.is_admin()), name='dispatch')
class TeacherUpdateView(UpdateView):
    model = CustomUser
    form_class = TeacherUpdateForm  # Utilisez TeacherUpdateForm au lieu de TeacherForm
    template_name = 'users/admin/user_form.html'
    extra_context = {
        'title': 'Modifier Professeur',
        'cancel_url': reverse_lazy('utilisateurs:teachers_list'),
    }
    def get_initial(self):
        initial = super().get_initial()
        # Convertit la date de naissance en format ISO pour être compatible avec le champ date
        if self.object.date_of_birth:
            initial['date_of_birth'] = self.object.date_of_birth.strftime('%Y-%m-%d')
        return initial
    
    def get_success_url(self):
        return self.extra_context['cancel_url']

@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(lambda u: u.is_admin()), name='dispatch')
class StudentUpdateView(UpdateView):
    model = CustomUser
    form_class = StudentUpdateForm  # Utilisez StudentUpdateForm au lieu de StudentForm
    template_name = 'users/admin/user_form.html'
    extra_context = {
        'title': 'Modifier Étudiant',
        'cancel_url': reverse_lazy('utilisateurs:students_list'),
    }

    def get_initial(self):
        initial = super().get_initial()
        # Convertit la date de naissance en format ISO pour être compatible avec le champ date
        if self.object.date_of_birth:
            initial['date_of_birth'] = self.object.date_of_birth.strftime('%Y-%m-%d')
        return initial
    def get_success_url(self):
        return self.extra_context['cancel_url']

@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(lambda u: u.is_admin()), name='dispatch')
class ParentUpdateView(UpdateView):
    model = CustomUser
    form_class = ParentUpdateForm  # Utilisez ParentUpdateForm au lieu de ParentForm
    template_name = 'users/admin/user_form.html'
    extra_context = {
        'title': 'Modifier Parent',
        'cancel_url': reverse_lazy('utilisateurs:parents_list'),
    }

    def get_initial(self):
        initial = super().get_initial()
        # Convertit la date de naissance en format ISO pour être compatible avec le champ date
        if self.object.date_of_birth:
            initial['date_of_birth'] = self.object.date_of_birth.strftime('%Y-%m-%d')
        return initial
    
    def get_success_url(self):
        return self.extra_context['cancel_url']
        
@method_decorator([login_required, user_passes_test(lambda u: u.is_admin())], name='dispatch')
class AdminDeleteView(DeleteView):
    model = CustomUser
    template_name = 'users/admin/user_confirm_delete.html'
    success_url = reverse_lazy('utilisateurs:admins_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.object  # Passer l'utilisateur actuel dans le contexte
        context['cancel_url'] = self.success_url
        return context


@method_decorator([login_required, user_passes_test(lambda u: u.is_admin())], name='dispatch')
class TeacherDeleteView(DeleteView):
    model = CustomUser
    template_name = 'users/admin/user_confirm_delete.html'
    success_url = reverse_lazy('utilisateurs:teachers_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.object  # Passer l'utilisateur actuel dans le contexte
        context['cancel_url'] = self.success_url
        return context

@method_decorator([login_required, user_passes_test(lambda u: u.is_admin())], name='dispatch')
class StudentDeleteView(DeleteView):
    model = CustomUser
    template_name = 'users/admin/user_confirm_delete.html'
    success_url = reverse_lazy('utilisateurs:students_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.object  # Passer l'utilisateur actuel dans le contexte
        context['cancel_url'] = self.success_url
        return context

@method_decorator([login_required, user_passes_test(lambda u: u.is_admin())], name='dispatch')
class ParentDeleteView(DeleteView):
    model = CustomUser
    template_name = 'users/admin/user_confirm_delete.html'
    success_url = reverse_lazy('utilisateurs:parents_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.object  # Passer l'utilisateur actuel dans le contexte
        context['cancel_url'] = self.success_url
        return context
