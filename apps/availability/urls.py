from django.urls import path
from apps.availability.views import (
    AvailabilityRequestListView,
    CreateAvailabilityRequestView,
    create_availability_request,
    UpdateAvailabilityRequestView,
    update_availability_request,  # URL de soumission pour la modification
    AvailabilityRequestDeleteView,
    TeacherAvailabilityRequestListView,
    TeacherAvailabilityPendingRequestView,
    accept_availability_request,
    get_filieres,
    get_teachers_for_subject,
    reject_availability_request,
)

app_name = 'availability'

urlpatterns = [
    # Liste des demandes
    path('availability-requests/', AvailabilityRequestListView.as_view(), name='availability_request_list'),
    
    # Création
    path('create-request/', CreateAvailabilityRequestView.as_view(), name='create_request'),
    path('create-availability-request/', create_availability_request, name='create_availability_request'),
    
    # Modification (GET) et mise à jour (POST)
    path('availability/update/<int:pk>/', UpdateAvailabilityRequestView.as_view(), name='availability_request_update'),
    path('update-availability-request/<int:pk>/', update_availability_request, name='update_availability_request'),
    
    # Suppression
    path('availability-request/delete/<int:pk>/', AvailabilityRequestDeleteView.as_view(), name='availability_request_delete'),
    
    # Requêtes AJAX pour chargement dynamique
    path('ajax/get-teachers/', get_teachers_for_subject, name='get_teachers_for_subject'),
    path('ajax/get-filieres/', get_filieres, name='get_filieres'),
    
    # Vues pour les enseignants
    path('teacher/availability/history/', TeacherAvailabilityRequestListView.as_view(), name='teacher_availability_request_list'),
    path('teacher/availability/pending/', TeacherAvailabilityPendingRequestView.as_view(), name='teacher_availability_pending_request_list'),
    path('teacher/availability/request/accept/<int:request_id>/', accept_availability_request, name='accept_availability_request'),
    path('teacher/availability/request/reject/<int:request_id>/', reject_availability_request, name='reject_availability_request'),
]