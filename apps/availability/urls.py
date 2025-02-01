from django.urls import path
from apps.availability.views import AvailabilityRequestDeleteView, AvailabilityRequestListView, AvailabilityRequestUpdateView, CreateAvailabilityRequestView, TeacherAvailabilityRequestListView, create_availability_request, get_filieres, get_teachers_for_subject

app_name='availability'

urlpatterns = [
    
    path('availability-requests/', AvailabilityRequestListView.as_view(), name='availability_request_list'),
    
    path('create-request/', CreateAvailabilityRequestView.as_view(), name='create_request'),
    
    path('create-availability-request/', create_availability_request, name='create_availability_request'),
    path('ajax/get-teachers/', get_teachers_for_subject, name='get_teachers_for_subject'),
    path('ajax/get-filieres/', get_filieres, name='get_filieres'), 
    
    path('availability-request/delete/<int:pk>/', AvailabilityRequestDeleteView.as_view(), name='availability_request_delete'),
    path('availability-request/edit/<int:pk>/', AvailabilityRequestUpdateView.as_view(), name='availability_request_edit'),
    
    path('teacher/requests/', TeacherAvailabilityRequestListView.as_view(), name='teacher_availability_request_list'),
    # path('teacher/request/<int:pk>/<str:action>/', AvailabilityRequestAcceptRejectView.as_view(), name='accept_reject_availability_request'),

]
