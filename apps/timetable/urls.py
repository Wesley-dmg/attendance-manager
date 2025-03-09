from django.urls import path
from apps.availability.views import get_filieres, get_teachers
from apps.timetable.utils import download_timetable, timetable_default_redirect
from apps.timetable.views import   CourseSessionAddMoreView, TimetableListView, TimetableDetailView,CourseSessionCreateView,CourseSessionUpdateView,TimetableDeleteView
from django.views.generic import TemplateView

app_name = 'timetables'

urlpatterns = [
    
    path('', timetable_default_redirect, name='timetable_default'),
    path("<int:pk>/download/", download_timetable, name="timetable_download"),  # Correct ici

    path("list", TimetableListView.as_view(), name="timetable_list"),
    path('<int:pk>/', TimetableDetailView.as_view(), name='timetable_detail'),

    path("create/", CourseSessionCreateView.as_view(), name="timetable_create"),
    path('<int:timetable_id>/add-more/', CourseSessionAddMoreView.as_view(), name='add_more'),
    path("<int:pk>/edit/", CourseSessionUpdateView.as_view(), name="timetable_edit"),
    path("<int:pk>/delete/", TimetableDeleteView.as_view(), name="timetable_delete"),
    
    # /timetables/<int:pk>/ => on affiche la DetailView du Timetable
    path('no-timetable/', TemplateView.as_view(template_name="timetable/admin/no_timetable.html"), name='no_timetable_page'),
    
    path('ajax/get-teachers/', get_teachers, name='get_teachers'),
    path('ajax/get-filieres/', get_filieres, name='get_filieres'),
    

]
