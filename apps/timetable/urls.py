from django.urls import path
from apps.timetable.utils import timetable_default_redirect
from apps.timetable.views import TimetableDetailView
from django.views.generic import TemplateView

app_name = 'timetables'  # Namespace for this application

urlpatterns = [
    
    path('timetables/', timetable_default_redirect, name='timetable_default'),

    # /timetables/<int:pk>/ => on affiche la DetailView du Timetable
    path('timetables/<int:pk>/', TimetableDetailView.as_view(), name='timetable_detail'),
    path('timetables/no-timetable/', TemplateView.as_view(template_name="timetable/no_timetable.html"), name='no_timetable_page'),

]
