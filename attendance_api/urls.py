from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from attendance_api.views.auth import RequestOTPView, ResendOTPView, VerifyOTPView
from attendance_api.views.courses import SubjectDepartmentsView
from attendance_api.views.presence import CreateAttendanceView, TeacherSubjectsView
from attendance_api.views.students import StudentsByDepartmentsView

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    path('teacher/request-otp/', RequestOTPView.as_view(), name='request-otp'),
    path('teacher/verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
    path('teacher/resend-otp/', ResendOTPView.as_view(), name='resend-otp'),
    
    path("teacher/subjects/", TeacherSubjectsView.as_view(), name="teacher-subjects"),
    
    path("teacher/subject/<int:subject_id>/departments/", SubjectDepartmentsView.as_view(), name="subject-departments"),
    
    path("teacher/students/", StudentsByDepartmentsView.as_view(), name="students-by-departments"),
    
    path("teacher/attendance/", CreateAttendanceView.as_view(), name="create-attendance"),

]