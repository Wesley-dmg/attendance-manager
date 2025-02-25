# from django.shortcuts import render
# from django.utils.decorators import method_decorator
# from django.contrib.auth.decorators import user_passes_test,login_required
# views.py

from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView,CreateView, UpdateView, DeleteView 
from apps.timetable.models import CourseSession, Timetable
from django.shortcuts import get_object_or_404
from django.http import HttpResponse

class TimetableListView(ListView):
    model = Timetable
    template_name = "timetable/timetable_list.html"
    context_object_name = "timetables"

    def get_queryset(self):
        return Timetable.objects.prefetch_related("department_levels").order_by("-start_date")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Liste des Emplois du Temps'
        context["create_url"] = "timetables:timetable_create"
        context["edit_url"] = "timetables:timetable_edit"
        context["delete_url"] = "timetables:timetable_delete"
        context["detail_url"] = "timetables:timetable_detail"
        context["download_url"] = "timetables:timetable_download"
        return context
    
class TimetableDetailView(DetailView):
    model = Timetable
    template_name = 'timetable/detail.html'
    context_object_name = 'timetable'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        timetable = self.object

        # Récupérer toutes les sessions de cours associées à cet emploi du temps
        course_sessions = (CourseSession.objects
                           .filter(timetable=timetable)
                           .select_related('subject', 'teacher', 'room', 'room__building', 'room__floor')
                           .order_by('room__building__name', 'room__floor__number', 'room__room_number'))

        # Organiser les sessions par bâtiment et étage
        structure = {}
        for session in course_sessions:
            building = session.room.building.name
            floor = f"{session.room.floor.number}ème Étage"
            room = f"N°{session.room.room_number}"

            if building not in structure:
                structure[building] = {}

            if floor not in structure[building]:
                structure[building][floor] = {}

            if room not in structure[building][floor]:
                structure[building][floor][room] = []

            structure[building][floor][room].append(session)

        context['structured_sessions'] = structure
        return context



class TimetableCreateView(CreateView):
    model = Timetable
    fields = ['start_date', 'end_date', 'room', 'subject', 'teacher', 'level']
    template_name = 'timetables/timetable_form.html'
    success_url = reverse_lazy('timetables:list')  # Redirige après la création

class TimetableUpdateView(UpdateView):
    model = Timetable
    fields = ['start_date', 'end_date', 'room', 'subject', 'teacher', 'level']
    template_name = 'timetables/timetable_form.html'
    success_url = reverse_lazy('timetables:list')


class TimetableDeleteView(DeleteView):
    model = Timetable
    template_name = 'timetables/timetable_confirm_delete.html'
    success_url = reverse_lazy('timetables:list')
