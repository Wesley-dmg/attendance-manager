from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import TemplateView, DetailView, FormView
from apps.attendance.models import Attendance
from apps.courses.models import Department, DepartmentLevel
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
            # Récupère le profil enseignant
            teacher_profile = user.teacherprofile

            # Matières enseignées
            subjects = teacher_profile.subjects.all()

            # DepartmentLevels concernés par les matières du prof
            department_levels = DepartmentLevel.objects.filter(
                department_levels_subjects__subject__in=subjects
            ).distinct()

            # Étudiants inscrits dans ces niveaux de département
            students = StudentProfile.objects.filter(
                major__in=department_levels
            ).distinct()

            # Absences enregistrées par cet enseignant, dans ses matières, pour ses étudiants
            absences = Attendance.objects.filter(
                teacher=teacher_profile,
                subject__in=subjects,
                student__in=students,
                status="absent",
            )

            # Filières concernées = départements associés aux DepartmentLevel
            departments = Department.objects.filter(
                department_levels__in=department_levels
            ).distinct()

            # Ajout au context
            context["total_students"] = students.count()
            context["total_absences"] = absences.count()
            context["total_streams"] = departments.count()
            context["subjects"] = subjects

        except TeacherProfile.DoesNotExist:
            context["total_students"] = 0
            context["total_absences"] = 0
            context["total_streams"] = 0
            context["subjects"] = []

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
        return self.render_to_response(self.get_context_data(form=form))

    def form_valid(self, form):
        selected_department_levels = self.request.POST.getlist("department_levels")
        if not selected_department_levels:
            form.add_error(None, "Veuillez sélectionner au moins une filière.")
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
