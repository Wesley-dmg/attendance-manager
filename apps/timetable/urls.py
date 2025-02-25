from django.urls import path
from apps.timetable.utils import download_timetable, timetable_default_redirect
from apps.timetable.views import TimetableCreateView, TimetableDeleteView, TimetableDetailView, TimetableListView, TimetableUpdateView
from django.views.generic import TemplateView

app_name = 'timetables'  # Namespace for this application

urlpatterns = [
    
    path('timetables/', timetable_default_redirect, name='timetable_default'),
    path("<int:pk>/download/", download_timetable, name="timetable_download"),  # Correct ici


    path("timetable/list", TimetableListView.as_view(), name="timetable_list"),
    path("create/", TimetableCreateView.as_view(), name="timetable_create"),
    path("<int:pk>/edit/", TimetableUpdateView.as_view(), name="timetable_edit"),
    path("<int:pk>/delete/", TimetableDeleteView.as_view(), name="timetable_delete"),
    
    # /timetables/<int:pk>/ => on affiche la DetailView du Timetable
    path('timetables/<int:pk>/', TimetableDetailView.as_view(), name='timetable_detail'),
    path('timetables/no-timetable/', TemplateView.as_view(template_name="timetable/no_timetable.html"), name='no_timetable_page'),

]
