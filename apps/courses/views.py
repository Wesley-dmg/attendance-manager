from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import user_passes_test,login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin

from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from apps.home.mixins import AdminTestMixin
from apps.courses.forms import DepartmentForm, DepartmentLevelForm, LevelForm
from apps.courses.models import Department, DepartmentLevel, Level

# CRUD for Department
class DepartmentListView(LoginRequiredMixin,PermissionRequiredMixin,AdminTestMixin,ListView):
    model = Department
    template_name = 'courses/department_list.html'
    permission_required= 'courses.view_department'
    extra_context = {
        'title': 'Liste des Filières',
        'create_url': 'courses:department_add',
        'edit_url': 'courses:department_edit',
        'delete_url': 'courses:department_delete',
    }

class DepartmentCreateView(LoginRequiredMixin,PermissionRequiredMixin,AdminTestMixin,CreateView):
    model = Department
    form_class = DepartmentForm
    template_name = 'courses/form_template.html'
    permission_required= 'courses.add_department'
    success_url = reverse_lazy('courses:department_list')
    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Ajouter une Filière'
        context['cancel_url'] = reverse_lazy('courses:department_list')
        return context

class DepartmentUpdateView(LoginRequiredMixin,PermissionRequiredMixin,AdminTestMixin,UpdateView):
    model = Department
    form_class = DepartmentForm
    template_name = 'courses/form_template.html'
    permission_required= 'courses.change_department'
    success_url = reverse_lazy('courses:department_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Modifier la Filière'
        context['cancel_url'] = reverse_lazy('courses:department_list')
        return context

class DepartmentDeleteView(LoginRequiredMixin,PermissionRequiredMixin,AdminTestMixin,DeleteView):
    model = Department
    template_name = 'courses/confirm_delete.html'
    permission_required= 'courses.delete_department'
    success_url = reverse_lazy('courses:department_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cancel_url'] = reverse_lazy('courses:department_list')
        return context

# CRUD for Level
class LevelListView(LoginRequiredMixin,PermissionRequiredMixin,AdminTestMixin,ListView):
    model = Level
    template_name = 'courses/level_list.html'
    permission_required= 'courses.view_level'
    extra_context = {
        'title': 'Liste des Niveaux d\'Étude',
        'create_url': 'courses:level_add',
        'edit_url': 'courses:level_edit',
        'delete_url': 'courses:level_delete',
    }

class LevelCreateView(LoginRequiredMixin,PermissionRequiredMixin,AdminTestMixin,CreateView):
    model = Level
    form_class = LevelForm
    template_name = 'courses/form_template.html'
    permission_required= 'courses.add_level'
    success_url = reverse_lazy('courses:level_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Ajouter un Niveaux d\'Études'
        context['cancel_url'] = reverse_lazy('courses:level_list')
        return context

class LevelUpdateView(LoginRequiredMixin,PermissionRequiredMixin,AdminTestMixin,UpdateView):
    model = Level
    form_class = LevelForm
    template_name = 'courses/form_template.html'
    permission_required= 'courses.change_level'
    success_url = reverse_lazy('courses:level_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Modifier le Niveau'
        context['cancel_url'] = reverse_lazy('courses:level_list')
        return context

class LevelDeleteView(LoginRequiredMixin,PermissionRequiredMixin,AdminTestMixin,DeleteView):
    model = Level
    template_name = 'courses/confirm_delete.html'
    permission_required= 'courses.delete_level'
    success_url = reverse_lazy('courses:level_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cancel_url'] = reverse_lazy('courses:level_list')
        return context

# CRUD for DepartmentLevel
class DepartmentLevelListView(LoginRequiredMixin,PermissionRequiredMixin,AdminTestMixin,ListView):
    model = DepartmentLevel
    template_name = 'courses/departmentlevel_list.html'
    permission_required= 'courses.view_departmentlevel'
    extra_context = {
        'title': 'Liste des Filières par Niveau',
        'create_url': 'courses:departmentlevel_add',
        'edit_url': 'courses:departmentlevel_edit',
        'delete_url': 'courses:departmentlevel_delete',
    }

class DepartmentLevelCreateView(LoginRequiredMixin,PermissionRequiredMixin,AdminTestMixin,CreateView):
    model = DepartmentLevel
    form_class = DepartmentLevelForm
    template_name = 'courses/form_template.html'
    permission_required= 'courses.add_departmentlevel'
    success_url = reverse_lazy('courses:departmentlevel_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Ajouter une Filière par Niveau'
        context['cancel_url'] = reverse_lazy('courses:departmentlevel_list')
        return context

class DepartmentLevelUpdateView(LoginRequiredMixin,PermissionRequiredMixin,AdminTestMixin,UpdateView):
    model = DepartmentLevel
    form_class = DepartmentLevelForm
    template_name = 'courses/form_template.html'
    permission_required= 'courses.change_departmentlevel'
    success_url = reverse_lazy('courses:departmentlevel_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Modifier la Filière par Niveau'
        context['cancel_url'] = reverse_lazy('courses:departmentlevel_list')
        return context

class DepartmentLevelDeleteView(LoginRequiredMixin,PermissionRequiredMixin,AdminTestMixin,DeleteView):
    model = DepartmentLevel
    template_name = 'courses/confirm_delete.html'
    permission_required= 'courses.delete_departmentlevel'
    success_url = reverse_lazy('courses:departmentlevel_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cancel_url'] = reverse_lazy('courses:departmentlevel_list')
        return context
