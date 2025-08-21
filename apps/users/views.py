import hashlib
from django.db import IntegrityError, transaction

from django.utils.http import urlencode

import random
import string

from django.shortcuts import render

from django.utils.text import slugify

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin

from django.shortcuts import get_object_or_404

from apps.attendance.models import Attendance
from apps.courses.models import DepartmentLevel
from apps.home.mixins import AdminTestMixin
from apps.users.utils import generate_reset_code, generate_unique_username

from .forms import UserUpdateForm
from django.contrib.auth import login, authenticate, update_session_auth_hash
from django.views.generic import (
    TemplateView,
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
    FormView,
)
from django.utils.translation import gettext as _
from django.shortcuts import render, redirect
from django.contrib.auth.views import *
from django.core.mail import send_mail
from django.urls import reverse, reverse_lazy

# from django.utils.decorators import method_decorator
from django.utils import timezone

from apps.home.utils import send_custom_message
from apps.users.forms import (
    AdminForm,
    AdminUpdateForm,
    CustomLoginForm,
    CustomPasswordChangeForm,
    CustomPasswordResetForm,
    CustomSetPasswordForm,
    CustomUserCreationForm,
    ParentForm,
    ParentUpdateForm,
    PasswordResetCodeForm,
    StudentForm,
    StudentUpdateForm,
    TeacherForm,
    TeacherUpdateForm,
)
from apps.users.models import (
    AdminProfile,
    CustomUser,
    ParentProfile,
    StudentArchiveHistory,
    StudentProfile,
    TeacherProfile,
)

from django.views import View

from django.contrib.auth import get_user_model, logout

from django.db.models import Q


def generate_password():
    characters = string.ascii_letters + string.digits + "!@#$%^&*()-_=+"
    return "".join(random.choice(characters) for _ in range(10))


class RoleLoginView(TemplateView):
    template_name = "accounts/choose_role.html"


# Vue pour l'inscription
# @user_passes_test(lambda u: u.is_authenticated and u.is_superuser)
def CustomregisterView(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            send_custom_message(
                request,
                _(
                    "Compte administrateur créé avec succès. Vous pouvez maintenant vous connecter."
                ),
                "success",
            )
            return redirect("users:login")
        else:
            send_custom_message(
                request,
                _("Erreur lors de l'inscription. Veuillez vérifier les champs."),
                "error",
            )
    else:
        form = CustomUserCreationForm()
    return render(request, "accounts/auth-signup.html", {"form": form})


# Ajoute les redirections pour chaque rôle dans un dictionnaire pour plus de lisibilité
ROLE_REDIRECTS = {
    "admin": "home:dashboard",
}


# Vue pour la connexion
def CustomLoginView(request):
    # Récupérer le paramètre 'next' depuis GET (lorsque la page est chargée)
    next_url = request.GET.get("next", "")

    if request.method == "POST":
        form = CustomLoginForm(data=request.POST)
        # Prioriser le 'next' transmis via POST
        next_url = request.POST.get("next", next_url)

        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")

            user = authenticate(request, username=username, password=password)
            if user is not None:
                if user.role != "admin":
                    send_custom_message(
                        request,
                        _("Accès refusé. Vous n'êtes pas un administrateur."),
                        "error",
                    )
                    return redirect("users:login")

                if user.first_login:
                    user.first_login = False
                    user.first_login_date = timezone.now()
                    user.save()

                login(request, user)
                send_custom_message(
                    request, _("Vous êtes maintenant connecté."), "success"
                )

                # Si un 'next' existe et est valide, redirigez vers celui-ci, sinon redirigez selon le rôle
                if next_url:
                    return redirect(next_url)
                else:
                    return redirect(ROLE_REDIRECTS.get(user.role, "home:index"))
            else:
                send_custom_message(
                    request, _("Nom d'utilisateur ou mot de passe incorrect."), "error"
                )

        else:
            send_custom_message(
                request,
                _("Erreur dans le formulaire. Vérifiez vos informations."),
                "error",
            )
    else:
        form = CustomLoginForm()

    return render(
        request, "accounts/auth-signin.html", {"form": form, "next": next_url}
    )


# Vue pour le changement de mot de passe
class CustomPasswordChangeView(PasswordChangeView):
    form_class = CustomPasswordChangeForm
    template_name = "accounts/auth-change-password.html"
    success_url = reverse_lazy("users:login")

    def form_valid(self, form):
        user = form.save()
        update_session_auth_hash(self.request, user)
        user.mark_password_as_changed()
        send_custom_message(
            self.request, _("Votre mot de passe a été changé avec succès."), "success"
        )
        return super().form_valid(form)


# Vue pour la demande de réinitialisation du mot de passe
class CustomPasswordResetView(PasswordResetView):
    form_class = CustomPasswordResetForm
    template_name = "accounts/auth-reset-password.html"
    success_url = reverse_lazy("users:password_reset_code")

    def form_valid(self, form):
        email = form.cleaned_data["email"]
        user = CustomUser.objects.filter(email=email).first()

        if not user:
            send_custom_message(
                self.request, _("Aucun utilisateur trouvé avec cet email."), "error"
            )
            return self.form_invalid(form)

        # ✅ Génération sécurisée du code
        code, hashed_code = generate_reset_code()
        user.reset_code = hashed_code
        user.reset_code_expiry = timezone.now() + timezone.timedelta(minutes=5)
        user.save(update_fields=["reset_code", "reset_code_expiry"])

        # ✅ Envoie du code par email
        send_mail(
            "Code de réinitialisation de votre mot de passe",
            f"Votre code de réinitialisation est : {code}",
            "from@example.com",
            [email],
            fail_silently=False,
        )

        send_custom_message(
            self.request,
            _("Un code de réinitialisation a été envoyé par email."),
            "success",
        )

        return redirect(self.success_url)


# Vue pour réinitialiser le mot de passe
class CustomPasswordResetConfirmView(FormView):
    template_name = "accounts/auth-password-reset-confirm.html"
    form_class = CustomSetPasswordForm
    success_url = reverse_lazy("users:login")

    def dispatch(self, request, *args, **kwargs):
        """
        Vérifie si l'ID de l'utilisateur est dans la session.
        Si ce n'est pas le cas, redirige vers la demande de réinitialisation.
        """
        self.user_id = request.session.get("reset_user_id")
        if not self.user_id:
            send_custom_message(
                self.request,
                _(
                    "Session expirée. Veuillez recommencer le processus de réinitialisation."
                ),
                "error",
            )
            return redirect("users:password_reset")
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        """
        Fournit des arguments au formulaire, y compris l'utilisateur chargé à partir de l'ID en session.
        """
        kwargs = super().get_form_kwargs()
        kwargs["user"] = CustomUser.objects.get(
            id=self.user_id
        )  # Charge l'utilisateur en fonction de l'ID en session
        return kwargs

    def form_valid(self, form):
        """
        Enregistre le nouveau mot de passe et nettoie la session.
        """
        form.save()  # Met à jour le mot de passe de l'utilisateur
        send_custom_message(
            self.request,
            _("Votre mot de passe a été mis à jour avec succès."),
            "success",
        )
        del self.request.session["reset_user_id"]  # Nettoie la session pour la sécurité
        return super().form_valid(form)


class PasswordResetCodeView(View):
    template_name = "accounts/password_reset_code.html"
    form_class = PasswordResetCodeForm

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            code = form.cleaned_data["code"].upper()
            now = timezone.now()

            # ✅ Vérifie le hash du code
            hashed_code = hashlib.sha256(code.encode()).hexdigest()
            user = CustomUser.objects.filter(reset_code=hashed_code).first()

            if user:
                if user.reset_code_expiry and user.reset_code_expiry < now:
                    send_custom_message(
                        request,
                        _("Le code a expiré. Veuillez en redemander un nouveau."),
                        "error",
                    )
                    return render(request, self.template_name, {"form": form})

                # ✅ Code valide
                request.session["reset_user_id"] = user.id
                user.reset_code = None
                user.reset_code_expiry = None
                user.save(update_fields=["reset_code", "reset_code_expiry"])

                send_custom_message(
                    request,
                    _(
                        "Code validé. Vous pouvez maintenant définir un nouveau mot de passe."
                    ),
                    "success",
                )
                return redirect("users:password_reset_confirm")
            else:
                send_custom_message(
                    request, _("Code de réinitialisation invalide."), "error"
                )

        return render(request, self.template_name, {"form": form})


def custom_logout(request):
    # On récupère le rôle avant de supprimer la session
    role = None
    if request.user.is_authenticated:
        role = request.user.role

    # Déconnexion
    logout(request)

    # Message
    send_custom_message(request, _("Vous êtes déconnecté avec succès."), "success")

    # Redirection selon le rôle
    if role == "teacher":
        return redirect(reverse("attendance:request-otp"))
    elif role == "student":
        return redirect(reverse("attendance:request-otp"))
    elif role == "parent":
        return redirect(reverse("attendance:request-otp"))
    else:
        return redirect(reverse("users:login"))


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = "users/profiles.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Ajouter le profil en fonction du rôle
        if user.is_teacher:
            context["profile"] = get_object_or_404(TeacherProfile, user=user)
        elif user.is_student:
            context["profile"] = get_object_or_404(StudentProfile, user=user)
        elif user.is_parent:
            context["profile"] = get_object_or_404(ParentProfile, user=user)
        elif user.is_admin:
            context["profile"] = get_object_or_404(AdminProfile, user=user)
        else:
            context["profile"] = None  # Aucun profil associé

        # Ajouter le formulaire de mise à jour dans le contexte
        context["form"] = UserUpdateForm(instance=user)
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = CustomUser
    form_class = UserUpdateForm
    template_name = "users/profiles.html"
    success_url = reverse_lazy("users:profiles")

    def get_object(self, queryset=None):
        return self.request.user


# Liste
class UserListView(LoginRequiredMixin, AdminTestMixin, ListView):
    model = CustomUser
    context_object_name = "users"
    template_name = "users/admin/liste.html"


class AdminListView(UserListView):
    # template_name = "users/admin/admins_list.html"
    permission_required = "users.view_adminprofile"
    extra_context = {
        "role": "admin",
        "title": "Liste des Administrateurs",
        "create_url": reverse_lazy("users:create_admin"),
        "detail_url": "users:admin_detail",
        "edit_url": "users:edit_admin",
        "delete_url": "users:delete_admin",
    }

    def get_queryset(self):
        return CustomUser.objects.filter(role="admin")


class TeacherListView(UserListView):
    permission_required = "users.view_teacherprofile"
    extra_context = {
        "role": "teacher",
        "title": "Liste des Professeurs",
        "detail_url": "users:teacher_detail",
        "create_url": reverse_lazy("users:create_teacher"),
        "edit_url": "users:edit_teacher",
        "delete_url": "users:delete_teacher",
    }

    def get_queryset(self):
        return CustomUser.objects.filter(role="teacher").select_related(
            "teacherprofile"
        )


class StudentListView(UserListView):
    permission_required = "users.view_studentprofile"
    extra_context = {
        "role": "student",
        "title": "Liste des Étudiants",
        "create_url": reverse_lazy("users:create_student"),
        "detail_url": "users:student_detail",
        "edit_url": "users:edit_student",
        "delete_url": "users:delete_student",
    }

    def get_queryset(self):
        return CustomUser.objects.filter(role="student")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["filieres"] = DepartmentLevel.objects.all()
        return context


class ParentListView(UserListView):
    permission_required = "users.view_parentprofile"
    extra_context = {
        "role": "parent",
        "create_url": reverse_lazy("users:create_parent"),
        "title": "Liste des Parents",
        "detail_url": "users:parent_detail",
        "edit_url": "users:edit_parent",
        "delete_url": "users:delete_parent",
    }

    def get_queryset(self):
        return CustomUser.objects.filter(role="parent")


class AdminDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = CustomUser
    template_name = "users/admin/admin_detail.html"
    context_object_name = "user_obj"
    permission_required = "users.view_customuser"

    extra_context = {
        "title": _("Détails de l'administrateur"),
        "cancel_url": reverse_lazy("users:admins_list"),  # liste des admins
    }


class TeacherDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = CustomUser
    template_name = "users/admin/teacher_detail.html"
    context_object_name = "user_obj"
    permission_required = "users.view_teacherprofile"

    extra_context = {
        "title": _("Détails de l'enseignant"),
        "cancel_url": reverse_lazy("users:teachers_list"),
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        teacher_profile = get_object_or_404(TeacherProfile, user=self.object)
        context["teacher_profile"] = teacher_profile
        return context


class StudentDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = CustomUser
    template_name = "users/admin/student_detail.html"
    context_object_name = "user_obj"
    permission_required = "users.view_studentprofile"

    extra_context = {
        "title": _("Détails de l'étudiant"),
        "cancel_url": reverse_lazy("users:students_list"),
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student_profile = getattr(self.object, "studentprofile", None)
        context["student_profile"] = student_profile

        # Parents associés
        parents = ParentProfile.objects.filter(children=student_profile)
        context["parents"] = parents

        # Absences de l'étudiant
        if student_profile:
            absences = Attendance.objects.filter(student=student_profile).order_by(
                "-date"
            )
            context["attendances"] = absences

            # Historique d'archivage
            archive_history = StudentArchiveHistory.objects.filter(
                student=student_profile
            ).order_by("-performed_at")
            context["archive_history"] = archive_history

        return context


class ParentDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = CustomUser
    template_name = "users/admin/parent_detail.html"
    context_object_name = "user_obj"
    permission_required = "users.view_parentprofile"

    extra_context = {
        "title": _("Détails du parent"),
        "cancel_url": reverse_lazy("users:parents_list"),
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        parent_profile = getattr(self.object, "parentprofile", None)
        context["parent_profile"] = parent_profile

        # Récupérer les enfants associés
        children = parent_profile.children.all() if parent_profile else []
        context["children"] = children
        return context


# Create
class UserCreateView(
    LoginRequiredMixin, PermissionRequiredMixin, AdminTestMixin, CreateView
):
    template_name = "users/admin/user_form.html"

    def form_valid(self, form):
        phone = form.cleaned_data.get("phone_number")
        first_name = form.cleaned_data.get("first_name")
        role = getattr(form.instance, "role", None) or form.cleaned_data.get("role")

        if not phone:
            form.add_error("phone_number", "Le numéro de téléphone est requis.")
            return self.form_invalid(form)

        User = get_user_model()

        # Bloquer uniquement si un autre utilisateur avec ce numéro existe ET ce n'est pas un parent
        if User.objects.filter(phone_number=phone).exists() and role != "parent":
            form.add_error("phone_number", "Un utilisateur avec ce numéro existe déjà.")
            return self.form_invalid(form)

        # Générer un username unique automatiquement à partir du prénom
        base_username = slugify(first_name) or "user"
        username = base_username
        suffix = random.randint(10, 99)

        while User.objects.filter(username=username).exists():
            suffix = random.randint(10, 99)
            username = f"{base_username}{suffix}"

        form.instance.username = username
        form.instance.set_unusable_password()

        try:
            user = form.save()
        except Exception as e:
            form.add_error(
                None, "Erreur inattendue lors de la création de l'utilisateur."
            )
            return self.form_invalid(form)

        send_custom_message(
            self.request,
            _(f"{user.role.capitalize()} créé avec succès."),
            "success",
        )

        return super().form_valid(form)


class AdminCreateView(UserCreateView):
    form_class = AdminForm
    permission_required = "users.add_adminprofile"
    success_url = reverse_lazy("users:admins_list")
    extra_context = {
        "role": "admin",
        "title": "Ajouter Administrateur",
        "cancel_url": success_url,
    }

    def form_invalid(self, form):
        # Message d'erreur si le formulaire est invalide
        send_custom_message(
            self.request,
            _(
                "Erreur dans le formulaire. Un profil Administrateur pour cet utilisateur existe déjà."
            ),
            "error",
        )
        return super().form_invalid(form)


class TeacherCreateView(UserCreateView):
    form_class = TeacherForm
    permission_required = "users.add_teacherprofile"
    success_url = reverse_lazy("users:teachers_list")
    extra_context = {
        "role": "teacher",
        "title": "Ajouter Enseignants",
        "cancel_url": success_url,
    }

    def form_invalid(self, form):
        # Message d'erreur si le formulaire est invalide
        send_custom_message(
            self.request,
            _(
                "Erreur dans le formulaire. Un profil enseignant pour cet utilisateur existe déjà."
            ),
            "error",
        )
        return super().form_invalid(form)


class StudentCreateView(UserCreateView):
    form_class = StudentForm
    permission_required = "users.add_studentprofile"
    success_url = reverse_lazy("users:parent_selector")

    extra_context = {
        "role": "student",
        "title": "Ajouter Élève",
        "cancel_url": reverse_lazy("users:students_list"),
    }

    def form_valid(self, form):
        response = super().form_valid(form)
        student_profile = self.object.studentprofile
        return redirect(f"{self.success_url}?student_id={student_profile.pk}")


class ParentCreateView(
    LoginRequiredMixin, PermissionRequiredMixin, AdminTestMixin, CreateView
):
    form_class = ParentForm
    template_name = "users/admin/user_form.html"
    permission_required = "users.add_parentprofile"

    extra_context = {
        "title": "Créer Parent",
        "cancel_url": reverse_lazy("users:parents_list"),
    }

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        student_id = self.request.GET.get("student_id")
        if student_id:
            try:
                student = StudentProfile.objects.get(pk=student_id)
                kwargs["student_instance"] = student
            except StudentProfile.DoesNotExist:
                pass
        # Création pure → on n’autorise pas un numéro déjà utilisé
        kwargs["allow_existing_phone"] = False
        return kwargs

    def form_invalid(self, form):
        # Si duplication téléphone → renvoyer vers la page intermédiaire avec message
        if "phone_number" in form.errors:
            student_id = self.request.GET.get("student_id")
            q = form.data.get("phone_number", "")

            send_custom_message(
                self.request,
                _(
                    "Un parent avec ce numéro existe déjà. Utilisez la recherche pour l'associer."
                ),
                "error",
            )

            params = {}
            if student_id:
                params["student_id"] = student_id
            if q:
                params["q"] = q

            url = reverse("users:parent_selector")
            if params:
                url = f"{url}?{urlencode(params)}"
            return redirect(url)

        return super().form_invalid(form)

    def form_valid(self, form):
        try:
            user = form.save()
        except IntegrityError:
            # Filet de sécurité si la contrainte unique du modèle déclenche malgré tout
            student_id = self.request.GET.get("student_id")
            q = form.cleaned_data.get("phone_number", "")
            send_custom_message(
                self.request,
                _(
                    "Ce numéro est déjà utilisé par un parent. Utilisez la recherche pour l'associer."
                ),
                "error",
            )
            params = {}
            if student_id:
                params["student_id"] = student_id
            if q:
                params["q"] = q
            url = reverse("users:parent_selector")
            if params:
                url = f"{url}?{urlencode(params)}"
            return redirect(url)
        except Exception as e:
            form.add_error(
                None, _("Erreur inattendue lors de la création du parent : ") + str(e)
            )
            return self.form_invalid(form)

        send_custom_message(self.request, _("Parent créé avec succès."), "success")
        return redirect(self.get_success_url())

    def get_success_url(self):
        # Tu peux garder ta redirection actuelle
        return reverse("users:students_list")


class ParentSelectorView(
    LoginRequiredMixin, PermissionRequiredMixin, AdminTestMixin, TemplateView
):
    template_name = "users/admin/parent_selector.html"
    permission_required = "users.view_parentprofile"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student_id = self.request.GET.get("student_id")
        query = self.request.GET.get("q")

        parents = CustomUser.objects.filter(role="parent")
        if query:
            parents = parents.filter(
                Q(first_name__icontains=query)
                | Q(last_name__icontains=query)
                | Q(phone_number__icontains=query)
            )

        context.update(
            {
                "student_id": student_id,
                "parents": parents,
                "query": query,
            }
        )
        return context


class UserUpdateView(
    LoginRequiredMixin, PermissionRequiredMixin, AdminTestMixin, UpdateView
):
    model = CustomUser
    template_name = "users/admin/user_form.html"

    def get_initial(self):
        initial = super().get_initial()
        if self.object.date_of_birth:
            initial["date_of_birth"] = self.object.date_of_birth.strftime("%Y-%m-%d")
        return initial

    def get_success_url(self):
        return self.extra_context["cancel_url"]

    def form_valid(self, form):
        phone = form.cleaned_data.get("phone_number")

        if not phone:
            form.add_error("phone_number", "Le numéro de téléphone est requis.")
            return self.form_invalid(form)

        User = get_user_model()
        qs = User.objects.filter(phone_number=phone).exclude(pk=self.object.pk)
        if qs.exists():
            form.add_error("phone_number", "Ce numéro est déjà utilisé.")
            return self.form_invalid(form)

        # # Toujours garder username = phone_number
        # form.instance.username = phone
        return super().form_valid(form)


class AdminUpdateView(UserUpdateView):
    form_class = AdminUpdateForm  # Utilisez AdminUpdateForm au lieu de AdminForm
    permission_required = "users.change_adminprofile"
    extra_context = {
        "title": "Modifier Administrateur",
        "cancel_url": reverse_lazy("users:admins_list"),
    }


class TeacherUpdateView(UserUpdateView):
    form_class = TeacherUpdateForm  # Utilisez TeacherUpdateForm au lieu de TeacherForm
    permission_required = "users.change_teacherprofile"
    extra_context = {
        "title": "Modifier Professeur",
        "cancel_url": reverse_lazy("users:teachers_list"),
    }


class StudentUpdateView(UserUpdateView):
    form_class = StudentUpdateForm
    permission_required = "users.change_studentprofile"

    extra_context = {
        "title": "Modifier Élève",
        "cancel_url": reverse_lazy("users:students_list"),
    }


class ParentUpdateView(UserUpdateView):
    form_class = ParentUpdateForm
    permission_required = "users.change_parentprofile"
    template_name = "users/admin/user_form.html"

    extra_context = {
        "title": "Modifier Parent",
        "cancel_url": reverse_lazy("users:parents_list"),
    }

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        student_id = self.request.GET.get("student_id")
        if student_id:
            try:
                kwargs["student_instance"] = StudentProfile.objects.get(pk=student_id)
            except StudentProfile.DoesNotExist:
                pass
        return kwargs

    def form_valid(self, form):
        response = super().form_valid(form)
        student_id = self.request.GET.get("student_id")
        if student_id:
            student = StudentProfile.objects.get(pk=student_id)
            self.object.parentprofile.children.add(student)
        return response


class UserDeleteView(
    LoginRequiredMixin, PermissionRequiredMixin, AdminTestMixin, DeleteView
):
    model = CustomUser
    template_name = "users/admin/user_confirm_delete.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user"] = self.object  # Passer l'utilisateur actuel dans le contexte
        context["cancel_url"] = self.success_url
        return context


class AdminDeleteView(UserDeleteView):
    permission_required = "users.delete_adminprofile"
    success_url = reverse_lazy("users:admins_list")


class TeacherDeleteView(UserDeleteView):
    permission_required = "users.delete_teacherprofile"
    success_url = reverse_lazy("users:teachers_list")


class StudentDeleteView(UserDeleteView):
    permission_required = "users.delete_studentprofile"
    success_url = reverse_lazy("users:students_list")


class ParentDeleteView(UserDeleteView):
    permission_required = "users.delete_parentprofile"
    success_url = reverse_lazy("users:parents_list")
