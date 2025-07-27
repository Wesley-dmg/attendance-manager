from django.contrib.auth import views as auth_views
from django.urls import path

from apps.courses.views import (
    DepartmentCreateView,
    DepartmentDeleteView,
    DepartmentLevelCreateView,
    DepartmentLevelDeleteView,
    DepartmentLevelListView,
    DepartmentLevelUpdateView,
    DepartmentListView,
    DepartmentUpdateView,
    LevelCreateView,
    LevelDeleteView,
    LevelListView,
    LevelUpdateView,
)


app_name = "courses"  # Namespace for this application


urlpatterns = [
    # Department URLs
    path("", DepartmentListView.as_view(), name="department_list"),
    path("add/", DepartmentCreateView.as_view(), name="department_add"),
    path("<int:pk>/edit/", DepartmentUpdateView.as_view(), name="department_edit"),
    path("<int:pk>/delete/", DepartmentDeleteView.as_view(), name="department_delete"),
    # Level URLs
    path("levels/", LevelListView.as_view(), name="level_list"),
    path("levels/add/", LevelCreateView.as_view(), name="level_add"),
    path("levels/<int:pk>/edit/", LevelUpdateView.as_view(), name="level_edit"),
    path("levels/<int:pk>/delete/", LevelDeleteView.as_view(), name="level_delete"),
    # DepartmentLevel URLs
    path(
        "departmentlevels/",
        DepartmentLevelListView.as_view(),
        name="departmentlevel_list",
    ),
    path(
        "departmentlevels/add/",
        DepartmentLevelCreateView.as_view(),
        name="departmentlevel_add",
    ),
    path(
        "departmentlevels/<int:pk>/edit/",
        DepartmentLevelUpdateView.as_view(),
        name="departmentlevel_edit",
    ),
    path(
        "departmentlevels/<int:pk>/delete/",
        DepartmentLevelDeleteView.as_view(),
        name="departmentlevel_delete",
    ),
]
