from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import user_passes_test,login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from apps.home.mixins import AdminTestMixin

from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.shortcuts import render, redirect
from django.urls import reverse_lazy

from apps.common.forms import DepartmentLevelSubjectForm
from apps.common.models import DepartmentLevelSubject

# CRUD for DepartmentLevelSubject
class DepartmentLevelSubjectListView(LoginRequiredMixin,PermissionRequiredMixin,AdminTestMixin,ListView):
    model = DepartmentLevelSubject
    template_name = 'common/departmentlevelsubject_list.html'
    permission_required= 'common.view_departmentlevelsubject'
    extra_context = {
        'title': 'Liste des Matières par Filière',
        'create_url':'common:departmentlevelsubject_add',
        'edit_url': 'common:departmentlevelsubject_edit',
        'delete_url': 'common:departmentlevelsubject_delete',
    }

class DepartmentLevelSubjectCreateView(LoginRequiredMixin,PermissionRequiredMixin,AdminTestMixin,CreateView):
    model = DepartmentLevelSubject
    form_class = DepartmentLevelSubjectForm
    permission_required= 'common.add_departmentlevelsubject'
    template_name = 'common/form_template.html'
    success_url = reverse_lazy('common:departmentlevelsubject_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Ajouter une Matière à la Filière et Niveau'
        context['cancel_url'] = reverse_lazy('common:departmentlevelsubject_list')
        return context

class DepartmentLevelSubjectUpdateView(LoginRequiredMixin,PermissionRequiredMixin,AdminTestMixin,UpdateView):
    model = DepartmentLevelSubject
    form_class = DepartmentLevelSubjectForm
    template_name = 'common/form_template.html'
    permission_required= 'common.change_departmentlevelsubject'
    success_url = reverse_lazy('common:departmentlevelsubject_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Modifier la Matière pour la Filière et Niveau'
        context['cancel_url'] = reverse_lazy('common:departmentlevelsubject_list')
        return context

class DepartmentLevelSubjectDeleteView(LoginRequiredMixin,PermissionRequiredMixin,AdminTestMixin,DeleteView):
    model = DepartmentLevelSubject
    template_name = 'common/confirm_delete.html'
    permission_required= 'common.delete_departmentlevelsubject'
    success_url = reverse_lazy('common:departmentlevelsubject_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cancel_url'] = reverse_lazy('common:departmentlevelsubject_list')
        return context
