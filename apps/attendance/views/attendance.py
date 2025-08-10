from django.utils import timezone
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import TemplateView

from apps.attendance.models import Attendance
from apps.subjects.models import Subject
from apps.users.models import StudentProfile

from django.contrib.auth.mixins import LoginRequiredMixin


class MarkAttendanceView(LoginRequiredMixin, TemplateView):
    template_name = "attendance/mark_attendance.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        subject_id = self.request.GET.get("subject")
        department_ids = self.request.GET.getlist("departments")

        try:
            subject = Subject.objects.get(pk=subject_id)
        except Subject.DoesNotExist:
            subject = None

        students = StudentProfile.objects.filter(major_id__in=department_ids)

        context["subject"] = subject
        context["department_ids"] = department_ids
        context["students"] = students
        return context

    def post(self, request, *args, **kwargs):
        subject_id = request.POST.get("subject")
        department_ids = request.POST.getlist("department_ids")
        absent_ids = request.POST.getlist("absent_students")

        subject = get_object_or_404(Subject, pk=subject_id)
        students = StudentProfile.objects.filter(major_id__in=department_ids)

        for student in students:
            status = "absent" if str(student.id) in absent_ids else "present"
            Attendance.objects.update_or_create(
                student=student,
                subject=subject,
                date=timezone.now().date(),
                defaults={
                    "status": status,
                    "teacher": request.user.teacherprofile,
                },
            )

        return redirect("attendance:dashboard")
