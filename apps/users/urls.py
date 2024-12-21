from django.views.generic import TemplateView
from django.urls import path
from .views import (
    CustomregisterView, CustomLoginView,CustomPasswordChangeView,CustomPasswordResetView, CustomPasswordResetConfirmView, PasswordResetCodeView,
    AdminListView, TeacherListView, StudentListView, ParentListView,
    AdminCreateView, TeacherCreateView, StudentCreateView, ParentCreateView,
    AdminUpdateView, TeacherUpdateView, StudentUpdateView, ParentUpdateView,
    AdminDeleteView, TeacherDeleteView, StudentDeleteView, ParentDeleteView
    
)

app_name = 'users'  # Nom de l'application pour les URL inversées

urlpatterns = [
    path('register/', CustomregisterView, name='register'),  # Inscription
    path('login/', CustomLoginView, name='login'),           # Connexion
    path('password_change/', CustomPasswordChangeView.as_view(), name='password_change'),  # Changement de mot de passe
    path('password_reset/', CustomPasswordResetView.as_view(), name='password_reset'),  # Demande de réinitialisation de mot de passe
    path('password_reset_done/', TemplateView.as_view(template_name='accounts/auth-password-change-done.html'), name='password_reset_done'),  # URL à ajouter
    path('reset_password_confirm/', CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),  # Nouveau mot de passe sans paramètres
    path('password_reset_code/', PasswordResetCodeView.as_view(), name='password_reset_code'),  # Vue pour entrer le code de validation
    
    path('admins/liste/', AdminListView.as_view(), name='admins_list'),
    path('teachers/liste/', TeacherListView.as_view(), name='teachers_list'),
    path('students/liste/', StudentListView.as_view(), name='students_list'),
    path('parents/liste/', ParentListView.as_view(), name='parents_list'),

    # Vues de création
    path('create/admin/', AdminCreateView.as_view(), name='create_admin'),
    path('create/teacher/', TeacherCreateView.as_view(), name='create_teacher'),
    path('create/student/', StudentCreateView.as_view(), name='create_student'),
    path('create/parent/', ParentCreateView.as_view(), name='create_parent'),

    # Vues de modification
    path('edit/admin/<int:pk>/', AdminUpdateView.as_view(), name='edit_admin'),
    path('edit/teacher/<int:pk>/', TeacherUpdateView.as_view(), name='edit_teacher'),
    path('edit/student/<int:pk>/', StudentUpdateView.as_view(), name='edit_student'),
    path('edit/parent/<int:pk>/', ParentUpdateView.as_view(), name='edit_parent'),

    # Vues de suppression
    path('delete/admin/<int:pk>/', AdminDeleteView.as_view(), name='delete_admin'),
    path('delete/teacher/<int:pk>/', TeacherDeleteView.as_view(), name='delete_teacher'),
    path('delete/student/<int:pk>/', StudentDeleteView.as_view(), name='delete_student'),
    path('delete/parent/<int:pk>/', ParentDeleteView.as_view(), name='delete_parent'),
    
]
