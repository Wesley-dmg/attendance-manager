from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import user_passes_test,login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.shortcuts import render, redirect
from django.urls import reverse_lazy

from apps.subjects.forms import SubjectForm
from apps.subjects.models import Subject
from apps.home.mixins import AdminTestMixin
# CRUD for Subject
class SubjectListView(LoginRequiredMixin,PermissionRequiredMixin,AdminTestMixin,ListView):
    model = Subject
    template_name = 'subjects/subject_list.html'
    permission_required= 'subjects.view_subject'
    extra_context = {
        'title': 'Liste des Matières',
        'create_url': 'subjects:subject_add',
        'edit_url': 'subjects:subject_edit',
        'delete_url': 'subjects:subject_delete',
    }

class SubjectCreateView(LoginRequiredMixin,PermissionRequiredMixin,AdminTestMixin,CreateView):
    model = Subject
    form_class = SubjectForm
    template_name = 'subjects/form_template.html'
    permission_required= 'subjects.add_subject'
    success_url = reverse_lazy('subjects:subject_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Ajouter une Matière'
        context['cancel_url'] = reverse_lazy('subjects:subject_list')
        return context

 
class SubjectUpdateView(LoginRequiredMixin,PermissionRequiredMixin,AdminTestMixin,UpdateView):
    model = Subject
    form_class = SubjectForm
    template_name = 'subjects/form_template.html'
    permission_required= 'subjects.change_subject'
    success_url = reverse_lazy('subjects:subject_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Modifier la Matière'
        context['cancel_url'] = reverse_lazy('subjects:subject_list')
        return context

class SubjectDeleteView(LoginRequiredMixin,PermissionRequiredMixin,AdminTestMixin,DeleteView):
    model = Subject
    template_name = 'subjects/confirm_delete.html'
    permission_required= 'subjects.delete_subject'
    success_url = reverse_lazy('subjects:subject_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cancel_url'] = reverse_lazy('subjects:subject_list')
        return context
