from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.shortcuts import render, redirect
from django.urls import reverse_lazy

from apps.common.forms import DepartmentLevelSubjectForm
from apps.common.models import DepartmentLevelSubject
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import user_passes_test,login_required

# @method_decorator([login_required, user_passes_test(lambda u: u.is_admin)], name='dispatch')

# CRUD for DepartmentLevelSubject
@method_decorator([login_required, user_passes_test(lambda u: u.is_admin)], name='dispatch')
class DepartmentLevelSubjectListView(ListView):
    model = DepartmentLevelSubject
    template_name = 'common/departmentlevelsubject_list.html'

class DepartmentLevelSubjectCreateView(CreateView):
    model = DepartmentLevelSubject
    form_class = DepartmentLevelSubjectForm
    template_name = 'common/form_template.html'
    success_url = reverse_lazy('common:departmentlevelsubject_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Ajouter une Matière à la Filière et Niveau'
        context['cancel_url'] = reverse_lazy('common:departmentlevelsubject_list')
        return context

class DepartmentLevelSubjectUpdateView(UpdateView):
    model = DepartmentLevelSubject
    form_class = DepartmentLevelSubjectForm
    template_name = 'common/form_template.html'
    success_url = reverse_lazy('common:departmentlevelsubject_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Modifier la Matière pour la Filière et Niveau'
        context['cancel_url'] = reverse_lazy('common:departmentlevelsubject_list')
        return context

class DepartmentLevelSubjectDeleteView(DeleteView):
    model = DepartmentLevelSubject
    template_name = 'common/confirm_delete.html'
    success_url = reverse_lazy('common:departmentlevelsubject_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cancel_url'] = reverse_lazy('common:departmentlevelsubject_list')
        return context
