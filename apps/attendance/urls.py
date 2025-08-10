from django.urls import path


from apps.attendance.views.attendance import MarkAttendanceView
from apps.attendance.views.auth import RequestOTPView, VerifyOTPView
from apps.attendance.views.subjects import (
    DashboardView,
    SubjectDepartmentSelectionView,
)


app_name = "attendance"  # Namespace for this application

urlpatterns = [
    path("signin/otp/", RequestOTPView.as_view(), name="request-otp"),
    path("login/verify/", VerifyOTPView.as_view(), name="verify-otp"),
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    path(
        "matieres/<int:pk>/filieres/",
        SubjectDepartmentSelectionView.as_view(),
        name="subject_departments",
    ),
    path("mark/", MarkAttendanceView.as_view(), name="mark"),
]
