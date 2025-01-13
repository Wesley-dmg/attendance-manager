from django.urls import path
from apps.availability.views import CreateAvailabilityRequestView, create_availability_request, get_filieres, get_teachers_for_subject

app_name='availability'

urlpatterns = [
    
    path('create-request/', CreateAvailabilityRequestView.as_view(), name='create_request'),
    
    path('create-availability-request/', create_availability_request, name='create_availability_request'),
    path('ajax/get-teachers/', get_teachers_for_subject, name='get_teachers_for_subject'),
    path('ajax/get-filieres/', get_filieres, name='get_filieres'), 
]
