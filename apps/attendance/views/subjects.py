from django.utils.translation import gettext as _
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import TemplateView, DetailView, FormView
from apps.attendance.models import Attendance
from apps.courses.models import Department, DepartmentLevel
from apps.home.utils import send_custom_message
from apps.users.models import StudentProfile, TeacherProfile

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404

from apps.attendance.forms.subjects_department import (
    DepartmentLevelChoiceForm,
)

from apps.common.models import DepartmentLevelSubject

from apps.subjects.models import Subject


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "attendance/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        try:
            teacher_profile = user.teacherprofile

            # Matières enseignées par ce prof
            subjects = teacher_profile.subjects.all()

            # Absences enregistrées par ce prof
            absences = Attendance.objects.filter(
                teacher=teacher_profile,
                status="absent",
            )

            # Étudiants concernés par ces absences
            students_concerned = StudentProfile.objects.filter(
                id__in=absences.values_list("student_id", flat=True)
            ).distinct()

            # Filières (DepartmentLevel) concernées
            department_levels = DepartmentLevel.objects.filter(
                id__in=students_concerned.values_list("major_id", flat=True)
            ).distinct()

            # Départements concernés
            departments = Department.objects.filter(
                department_levels__in=department_levels
            ).distinct()

            # Ajout au contexte
            context["subjects"] = subjects
            context["total_absences"] = absences.count()
            context["total_streams"] = department_levels.count()
            context["total_students"] = students_concerned.count()

        except TeacherProfile.DoesNotExist:
            context["subjects"] = []
            context["total_absences"] = 0
            context["total_streams"] = 0
            context["total_students"] = 0

        return context


class SubjectDepartmentSelectionView(LoginRequiredMixin, FormView):
    template_name = "attendance/subject_departments.html"
    form_class = DepartmentLevelChoiceForm

    def dispatch(self, request, *args, **kwargs):
        self.subject = get_object_or_404(Subject, pk=kwargs["pk"])
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        department_links = DepartmentLevelSubject.objects.filter(subject=self.subject)
        allowed_department_levels = [link.department_level for link in department_links]
        kwargs["allowed_department_levels"] = allowed_department_levels
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["subject"] = self.subject

        selected_department_levels = self.request.POST.getlist("department_levels")
        if selected_department_levels:
            students = StudentProfile.objects.filter(
                department_level_id__in=selected_department_levels
            )
            context["students"] = students

        return context

    def form_valid(self, form):
        send_custom_message(
            self.request,
            _("Formulaire validé."),
            "success",
        )
        return self.render_to_response(self.get_context_data(form=form))

    def form_valid(self, form):
        selected_department_levels = self.request.POST.getlist("department_levels")
        if not selected_department_levels:
            form.add_error(None, "Veuillez sélectionner au moins une filière.")
            send_custom_message(
                self.request,
                _("Veuillez sélectionner au moins une filière."),
                "warning",
            )
            return self.form_invalid(form)

        # Construit une URL avec les paramètres GET
        url = (
            reverse("attendance:mark")
            + f"?subject={self.subject.id}"
            + "".join(
                [f"&departments={dep_id}" for dep_id in selected_department_levels]
            )
        )
        return HttpResponseRedirect(url)
