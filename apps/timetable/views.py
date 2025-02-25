# from django.shortcuts import render
# from django.utils.decorators import method_decorator
# from django.contrib.auth.decorators import user_passes_test,login_required
# views.py

from django.views.generic import DetailView
from django.db.models import Max, Min
from apps.timetable.models import CourseSession, Timetable

# class TimetableDetailView(DetailView):
#     model = Timetable
#     template_name = 'timetables/detail.html'
#     context_object_name = 'timetable'  # le nom utilisé dans le template

#     def get_object(self, queryset=None):
#         """
#         S'il n'y a pas de pk dans l'URL, on renvoie le dernier Timetable.
#         Sinon, on renvoie le Timetable correspondant au pk.
#         """
#         if 'pk' not in self.kwargs:
#             # Pas de pk => on prend le dernier
#             return Timetable.objects.order_by('-start_date').first()
#         return super().get_object(queryset)

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         current_timetable = self.object  # Le Timetable affiché

#         # Récupérer le Timetable précédent (celui qui a start_date < current_timetable.start_date)
#         previous_timetable = (Timetable.objects.filter(start_date__lt=current_timetable.start_date)
#                               .order_by('-start_date').first())
        
#         context['previous_timetable'] = previous_timetable

#         # Récupérer le Timetable suivant (celui qui a start_date > current_timetable.start_date)
#         next_timetable = (Timetable.objects
#                           .filter(start_date__gt=current_timetable.start_date)
#                           .order_by('start_date')
#                           .first())
#         context['next_timetable'] = next_timetable

#         # pour la période couverte par current_timetable
#         context['course_sessions'] = current_timetable.course_sessions.all()
#         context['department_levels'] = current_timetable.department_levels.all()

#         return context

# class TimetableDetailView(DetailView):
#     model = Timetable
#     template_name = 'timetable/detail.html'
#     context_object_name = 'timetable'

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         timetable = self.object

#         # Timetable précédent (start_date < actuel)
#         previous_timetable = (Timetable.objects
#                               .filter(start_date__lt=timetable.start_date)
#                               .order_by('-start_date')
#                               .first())
#         context['previous_timetable'] = previous_timetable

#         # Timetable suivant (start_date > actuel)
#         next_timetable = (Timetable.objects
#                           .filter(start_date__gt=timetable.start_date)
#                           .order_by('start_date')
#                           .first())
#         context['next_timetable'] = next_timetable

#         # Autres données que tu veux passer au template...
#         return context


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
