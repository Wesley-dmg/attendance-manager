from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.shortcuts import render, redirect
from django.urls import reverse_lazy

from apps.subjects.forms import SubjectForm
from apps.subjects.models import Subject
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import user_passes_test,login_required

# CRUD for Subject
@method_decorator([login_required, user_passes_test(lambda u: u.is_admin)], name='dispatch')
class SubjectListView(ListView):
    model = Subject
    template_name = 'subjects/subject_list.html'
    extra_context = {
        'create_url': 'subjects:subject_add',
        'edit_url': 'subjects:subject_edit',
        'delete_url': 'subjects:subject_delete',
    }

@method_decorator([login_required, user_passes_test(lambda u: u.is_admin)], name='dispatch')
class SubjectCreateView(CreateView):
    model = Subject
    form_class = SubjectForm
    template_name = 'subjects/form_template.html'
    success_url = reverse_lazy('subjects:subject_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Ajouter une Matière'
        context['cancel_url'] = reverse_lazy('subjects:subject_list')
        return context

@method_decorator([login_required, user_passes_test(lambda u: u.is_admin)], name='dispatch')
class SubjectUpdateView(UpdateView):
    model = Subject
    form_class = SubjectForm
    template_name = 'subjects/form_template.html'
    success_url = reverse_lazy('subjects:subject_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Modifier la Matière'
        context['cancel_url'] = reverse_lazy('subjects:subject_list')
        return context

@method_decorator([login_required, user_passes_test(lambda u: u.is_admin)], name='dispatch')
class SubjectDeleteView(DeleteView):
    model = Subject
    template_name = 'subjects/confirm_delete.html'
    success_url = reverse_lazy('subjects:subject_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cancel_url'] = reverse_lazy('subjects:subject_list')
        return context

