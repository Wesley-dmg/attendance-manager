from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.shortcuts import render, redirect
from django.urls import reverse_lazy

from apps.subjects.forms import SubjectForm
from apps.subjects.models import Subject

# CRUD for Subject
class SubjectListView(ListView):
    model = Subject
    template_name = 'subjects/subject_list.html'

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

class SubjectDeleteView(DeleteView):
    model = Subject
    template_name = 'subjects/confirm_delete.html'
    success_url = reverse_lazy('subjects:subject_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cancel_url'] = reverse_lazy('subjects:subject_list')
        return context

