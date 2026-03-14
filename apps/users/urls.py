from django.urls import path
from django.views.generic import TemplateView

from apps.home.views import redirect_after_login
from apps.users.utils import (
    ParentSearchView,
    UserSearchView,
    check_parent_phone,
)
from .views import (
    AdminDetailView,
    CustomregisterView,
    CustomLoginView,
    CustomPasswordChangeView,
    CustomPasswordResetView,
    CustomPasswordResetConfirmView,
    ParentDetailView,
    ParentSelectorView,
    PasswordResetCodeView,
    AdminListView,
    ProfileUpdateView,
    ProfileView,
    RoleLoginView,
    StudentDetailView,
    TeacherDetailView,
    TeacherListView,
    StudentListView,
    ParentListView,
    AdminCreateView,
    TeacherCreateView,
    StudentCreateView,
    ParentCreateView,
    AdminUpdateView,
    TeacherUpdateView,
    StudentUpdateView,
    ParentUpdateView,
    AdminDeleteView,
    TeacherDeleteView,
    StudentDeleteView,
    ParentDeleteView,
    custom_logout,
    health_check,
    student_profile_pdf,
)

app_name = "users"  # Nom de l'application pour les URL inversées

urlpatterns = [
    path("", RoleLoginView.as_view(), name="choose_role"),
    path("login/", CustomLoginView, name="login"),
    path("register/", CustomregisterView, name="register"),  # Inscription
    path("logout/", custom_logout, name="logout"),
    path(
        "password_change/", CustomPasswordChangeView.as_view(), name="password_change"
    ),
    path(
        "password_reset/", CustomPasswordResetView.as_view(), name="password_reset"
    ),  # Demande de réinitialisation de mot de passe
    path(
        "password_reset_done/",
        TemplateView.as_view(template_name="accounts/auth-password-change-done.html"),
        name="password_reset_done",
    ),  # URL à ajouter
    path(
        "reset_password_confirm/",
        CustomPasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),  # Nouveau mot de passe sans paramètres
    path(
        "password_reset_code/",
        PasswordResetCodeView.as_view(),
        name="password_reset_code",
    ),  # Vue pour entrer le code de validation
    path("profiles/", ProfileView.as_view(), name="profiles"),
    path("profile/update/", ProfileUpdateView.as_view(), name="profile_update"),
    path("admins/liste/", AdminListView.as_view(), name="admins_list"),
    path("teachers/liste/", TeacherListView.as_view(), name="teachers_list"),
    path("students/liste/", StudentListView.as_view(), name="students_list"),
    path("parents/liste/", ParentListView.as_view(), name="parents_list"),
    # vues de details
    path("admins/<int:pk>/", AdminDetailView.as_view(), name="admin_detail"),
    # Vues de création
    path("create/admin/", AdminCreateView.as_view(), name="create_admin"),
    path("create/teacher/", TeacherCreateView.as_view(), name="create_teacher"),
    path("create/student/", StudentCreateView.as_view(), name="create_student"),
    path("create/parent/", ParentCreateView.as_view(), name="create_parent"),
    # Vues de modification
    path("edit/admin/<int:pk>/", AdminUpdateView.as_view(), name="edit_admin"),
    path("edit/teacher/<int:pk>/", TeacherUpdateView.as_view(), name="edit_teacher"),
    path("edit/student/<int:pk>/", StudentUpdateView.as_view(), name="edit_student"),
    path("edit/parent/<int:pk>/", ParentUpdateView.as_view(), name="edit_parent"),
    # Vues de suppression
    path("delete/admin/<int:pk>/", AdminDeleteView.as_view(), name="delete_admin"),
    path(
        "delete/teacher/<int:pk>/", TeacherDeleteView.as_view(), name="delete_teacher"
    ),
    path(
        "delete/student/<int:pk>/", StudentDeleteView.as_view(), name="delete_student"
    ),
    path("delete/parent/<int:pk>/", ParentDeleteView.as_view(), name="delete_parent"),
    path("admins/<int:pk>/", AdminDetailView.as_view(), name="admin_detail"),
    path("teachers/<int:pk>/", TeacherDetailView.as_view(), name="teacher_detail"),
    path("students/<int:pk>/", StudentDetailView.as_view(), name="student_detail"),
    path("student/<int:student_id>/pdf/", student_profile_pdf, name="student_pdf"),
    path("parents/<int:pk>/", ParentDetailView.as_view(), name="parent_detail"),
    path("check-parent-phone/", check_parent_phone, name="check_parent_phone"),
    path("redirect-after-login/", redirect_after_login, name="redirect-after-login"),
    path("search/", UserSearchView.as_view(), name="user_search"),
    path("search/parent/", ParentSearchView.as_view(), name="parent_search"),
    path("select/parent/", ParentSelectorView.as_view(), name="parent_selector"),
    path("health/", health_check, name="health_check"),
]
