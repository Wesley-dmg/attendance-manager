from django.contrib.auth import views as auth_views
from django.urls import path

from apps.subjects.views import SubjectCreateView, SubjectDeleteView, SubjectListView, SubjectUpdateView

app_name = 'subjects'  # Namespace for this application

urlpatterns = [   
    # Subject URLs
    path('subjects/', SubjectListView.as_view(), name='subject_list'),
    path('subjects/add/', SubjectCreateView.as_view(), name='subject_add'),
    path('subjects/<int:pk>/edit/', SubjectUpdateView.as_view(), name='subject_edit'),
    path('subjects/<int:pk>/delete/', SubjectDeleteView.as_view(), name='subject_delete'),

]
