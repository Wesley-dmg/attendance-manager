from django.urls import path
from apps.availability.views import CreateAvailabilityRequestView, create_availability_request, get_filieres, get_teachers_for_subject

app_name='availability'

urlpatterns = [
    
    path('create-request/', CreateAvailabilityRequestView.as_view(), name='create_request'),
    path('create-availability-request/', create_availability_request, name='create_availability_request'),
    path('ajax/get-teachers/', get_teachers_for_subject, name='get_teachers_for_subject'),
    path('ajax/get-filieres/', get_filieres, name='get_filieres'), 
    
    
    # Admin URLs
    # path('requests/create/', create_availability_request, name='create_availability_request'),
    # path('requests/add/', AvailabilityRequestCreateView.as_view(), name='admin_request_create'),
    # path('requests/', AvailabilityRequestListView.as_view(), name='admin_request_list'),
    # path('requests/<int:request_id>/', admin_request_detail, name='admin_request_detail'),
    # path('requests/<int:request_id>/delete/', admin_request_delete, name='admin_request_delete'),
    # Teacher URLs
    # path('teacher/requests/', TeacherRequestListView.as_view(), name='teacher_request_list'),
    # path('teacher/requests/<int:request_id>/<str:status>/', teacher_update_response, name='teacher_update_response'),
]
