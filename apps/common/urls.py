from django.contrib.auth import views as auth_views
from django.urls import path

from apps.common.views import DepartmentLevelSubjectCreateView, DepartmentLevelSubjectDeleteView, DepartmentLevelSubjectListView, DepartmentLevelSubjectUpdateView


app_name = 'common'  # Namespace for this application

urlpatterns = [   
    # DepartmentLevelSubject URLs
    path('', DepartmentLevelSubjectListView.as_view(), name='departmentlevelsubject_list'),
    path('add/', DepartmentLevelSubjectCreateView.as_view(), name='departmentlevelsubject_add'),
    path('<int:pk>/edit/', DepartmentLevelSubjectUpdateView.as_view(), name='departmentlevelsubject_edit'),
    path('<int:pk>/delete/', DepartmentLevelSubjectDeleteView.as_view(), name='departmentlevelsubject_delete'),
        
]
