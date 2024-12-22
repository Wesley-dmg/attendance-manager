from django.contrib.auth import views as auth_views
from django.urls import path

from apps.common.views import DepartmentLevelSubjectCreateView, DepartmentLevelSubjectDeleteView, DepartmentLevelSubjectListView, DepartmentLevelSubjectUpdateView


app_name = 'common'  # Namespace for this application

urlpatterns = [   
    # DepartmentLevelSubject URLs
    path('departmentlevelsubjects/', DepartmentLevelSubjectListView.as_view(), name='departmentlevelsubject_list'),
    path('departmentlevelsubjects/add/', DepartmentLevelSubjectCreateView.as_view(), name='departmentlevelsubject_add'),
    path('departmentlevelsubjects/<int:pk>/edit/', DepartmentLevelSubjectUpdateView.as_view(), name='departmentlevelsubject_edit'),
    path('departmentlevelsubjects/<int:pk>/delete/', DepartmentLevelSubjectDeleteView.as_view(), name='departmentlevelsubject_delete'),
        
]
