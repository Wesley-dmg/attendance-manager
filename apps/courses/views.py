from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.shortcuts import render, redirect
from django.urls import reverse_lazy

from apps.courses.forms import DepartmentForm, DepartmentLevelForm, LevelForm
from apps.courses.models import Department, DepartmentLevel, Level


# CRUD for Department
class DepartmentListView(ListView):
    model = Department
    template_name = 'courses/department_list.html'

class DepartmentCreateView(CreateView):
    model = Department
    form_class = DepartmentForm
    template_name = 'courses/form_template.html'
    success_url = reverse_lazy('courses:department_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Ajouter une Filière'
        context['cancel_url'] = reverse_lazy('courses:department_list')
        return context

class DepartmentUpdateView(UpdateView):
    model = Department
    form_class = DepartmentForm
    template_name = 'courses/form_template.html'
    success_url = reverse_lazy('courses:department_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Modifier la Filière'
        context['cancel_url'] = reverse_lazy('courses:department_list')
        return context

class DepartmentDeleteView(DeleteView):
    model = Department
    template_name = 'courses/confirm_delete.html'
    success_url = reverse_lazy('courses:department_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cancel_url'] = reverse_lazy('courses:department_list')
        return context


# CRUD for Level
class LevelListView(ListView):
    model = Level
    template_name = 'courses/level_list.html'

class LevelCreateView(CreateView):
    model = Level
    form_class = LevelForm
    template_name = 'courses/form_template.html'
    success_url = reverse_lazy('courses:level_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Ajouter un Niveau'
        context['cancel_url'] = reverse_lazy('courses:level_list')
        return context

class LevelUpdateView(UpdateView):
    model = Level
    form_class = LevelForm
    template_name = 'courses/form_template.html'
    success_url = reverse_lazy('courses:level_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Modifier le Niveau'
        context['cancel_url'] = reverse_lazy('courses:level_list')
        return context

class LevelDeleteView(DeleteView):
    model = Level
    template_name = 'courses/confirm_delete.html'
    success_url = reverse_lazy('courses:level_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cancel_url'] = reverse_lazy('courses:level_list')
        return context

# CRUD for DepartmentLevel
class DepartmentLevelListView(ListView):
    model = DepartmentLevel
    template_name = 'courses/departmentlevel_list.html'

class DepartmentLevelCreateView(CreateView):
    model = DepartmentLevel
    form_class = DepartmentLevelForm
    template_name = 'courses/form_template.html'
    success_url = reverse_lazy('courses:departmentlevel_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Ajouter une Filière par Niveau'
        context['cancel_url'] = reverse_lazy('courses:departmentlevel_list')
        return context

class DepartmentLevelUpdateView(UpdateView):
    model = DepartmentLevel
    form_class = DepartmentLevelForm
    template_name = 'courses/form_template.html'
    success_url = reverse_lazy('courses:departmentlevel_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Modifier la Filière par Niveau'
        context['cancel_url'] = reverse_lazy('courses:departmentlevel_list')
        return context

class DepartmentLevelDeleteView(DeleteView):
    model = DepartmentLevel
    template_name = 'courses/confirm_delete.html'
    success_url = reverse_lazy('courses:departmentlevel_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cancel_url'] = reverse_lazy('courses:departmentlevel_list')
        return context
