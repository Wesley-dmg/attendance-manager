
from django.shortcuts import redirect, get_object_or_404
from django.views.generic import ListView, DetailView,CreateView, UpdateView, DeleteView 
from django.views.generic.edit import FormView
from apps.home.utils import send_custom_message
from apps.timetable.models import CourseSession, Timetable, TimeSlot
from .forms import CourseSessionAdditionalForm, CourseSessionCreationForm
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.db import transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
import logging


class TimetableListView(ListView):
    model = Timetable
    template_name = "timetable/admin/timetable_list.html"
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

class CourseSessionCreateView(FormView):
    template_name = 'timetable/admin/coursesession_form.html'
    form_class = CourseSessionCreationForm

    def dispatch(self, request, *args, **kwargs):
        try:
            return super().dispatch(request, *args, **kwargs)
        except Exception as e:
            # Enregistrement de l'exception dans les logs
            logging.exception("Erreur lors du dispatch de la vue CourseSessionCreateView : %s", e)
            # Envoi d'un message d'erreur personnalisé
            send_custom_message(request, _("Une erreur inattendue est survenue. Veuillez réessayer."), 'error')
            # Vous pouvez choisir de rediriger ou de renvoyer un formulaire invalide
            return self.form_invalid(self.get_form())

    def form_valid(self, form):
        timetable_start_date = form.cleaned_data['timetable_start_date']
        timetable_end_date = form.cleaned_data['timetable_end_date']
        subject = form.cleaned_data['subject']
        department_levels = form.cleaned_data['department_levels']
        teacher = form.cleaned_data['teacher']
        room = form.cleaned_data['room']
        session_date = form.cleaned_data.get('session_date')
        timeslot = form.cleaned_data.get('timeslot')
        new_start_time = form.cleaned_data.get('new_start_time')
        new_end_time = form.cleaned_data.get('new_end_time')
        session_for_all_days = form.cleaned_data.get('session_for_all_days')

        with transaction.atomic():
            timetable, created = Timetable.objects.get_or_create(
                start_date=timetable_start_date,
                end_date=timetable_end_date
            )
            timetable.department_levels.set(department_levels)

            # Gestion des créneaux horaires
            if not timeslot:
                timeslot, created = TimeSlot.objects.get_or_create(
                    start_time=new_start_time,
                    end_time=new_end_time
                )

            # Vérification des conflits
            if CourseSession.objects.filter(
                timetable=timetable,
                teacher=teacher,
                date=session_date,
                timeslot=timeslot
            ).exists():
                send_custom_message(self.request, _("⚠️ Ce professeur est déjà occupé sur ce créneau horaire."),'error')
                return self.form_invalid(form)

            if CourseSession.objects.filter(
                timetable=timetable,
                room=room,
                date=session_date,
                timeslot=timeslot
            ).exists():
                send_custom_message(self.request, _("⚠️ Cette salle est déjà réservée à cette date et cet horaire."),'error')
                return self.form_invalid(form)

            # Création des sessions
            if session_for_all_days:
                current_date = timetable_start_date
                while current_date <= timetable_end_date:
                    CourseSession.objects.create(
                        timetable=timetable,
                        subject=subject,
                        teacher=teacher,
                        room=room,
                        date=current_date,
                        timeslot=timeslot,
                    )
                    current_date += timezone.timedelta(days=1)
                send_custom_message(self.request, _("✅ Sessions créées pour toute la période !"),'success')
            else:
                CourseSession.objects.create(
                    timetable=timetable,
                    subject=subject,
                    teacher=teacher,
                    room=room,
                    date=session_date,
                    timeslot=timeslot,
                )
                send_custom_message(self.request, _("✅ Session ajoutée avec succès !"),'success')

        return redirect(reverse_lazy('timetables:timetable_list'))

class CourseSessionUpdateView(FormView):
    template_name = 'timetable/admin/coursesession_form.html'
    form_class = CourseSessionCreationForm

    def get_object(self):
        return get_object_or_404(CourseSession, pk=self.kwargs.get('pk'))

    def get_initial(self):
        cs = self.get_object()
        timetable = cs.timetable
        return {
            'timetable_start_date': timetable.start_date,
            'timetable_end_date': timetable.end_date,
            'department_levels': timetable.department_levels.all(),
            'subject': cs.subject,
            'teacher': cs.teacher,
            'room': cs.room,
            'session_date': cs.date,
            'timeslot': cs.timeslot,
            'session_for_all_days': False,
        }

    def form_valid(self, form):
        cs = self.get_object()
        timetable = cs.timetable
        timetable_start_date = form.cleaned_data['timetable_start_date']
        timetable_end_date = form.cleaned_data['timetable_end_date']
        department_levels = form.cleaned_data['department_levels']
        subject = form.cleaned_data['subject']
        teacher = form.cleaned_data['teacher']
        room = form.cleaned_data['room']
        session_date = form.cleaned_data.get('session_date')
        timeslot = form.cleaned_data.get('timeslot')
        new_start_time = form.cleaned_data.get('new_start_time')
        new_end_time = form.cleaned_data.get('new_end_time')
        session_for_all_days = form.cleaned_data.get('session_for_all_days')

        with transaction.atomic():
            timetable.start_date = timetable_start_date
            timetable.end_date = timetable_end_date
            timetable.department_levels.set(department_levels)
            timetable.save()

            if not timeslot:
                timeslot, created = TimeSlot.objects.get_or_create(
                    start_time=new_start_time,
                    end_time=new_end_time
                )

            # Vérification des conflits avant modification
            if CourseSession.objects.exclude(pk=cs.pk).filter(
                timetable=timetable,
                teacher=teacher,
                date=session_date,
                timeslot=timeslot
            ).exists():
                send_custom_message(self.request, _("⚠️ Ce professeur est déjà occupé sur ce créneau horaire."),'error')
                return self.form_invalid(form)

            if CourseSession.objects.exclude(pk=cs.pk).filter(
                timetable=timetable,
                room=room,
                date=session_date,
                timeslot=timeslot
            ).exists():
                send_custom_message(self.request, _("⚠️ Cette salle est déjà réservée à cette date et cet horaire."),'error')
                return self.form_invalid(form)

            if session_for_all_days:
                CourseSession.objects.filter(timetable=timetable).update(
                    subject=subject,
                    teacher=teacher,
                    room=room,
                    timeslot=timeslot,
                )
                send_custom_message(self.request, _("✅ Toutes les sessions ont été mises à jour !"),'success')
            else:
                cs.subject = subject
                cs.teacher = teacher
                cs.room = room
                cs.date = session_date
                cs.timeslot = timeslot
                cs.save()
                send_custom_message(self.request, _("✅ Session modifiée avec succès !"),'success')

        return redirect(reverse_lazy('timetables:timetable_list'))
class CourseSessionAddMoreView(FormView):
    template_name = 'timetable/admin/coursesession_add_more_form.html'
    form_class = CourseSessionAdditionalForm
    
    def get_initial(self):
        initial = super().get_initial()
        # Récupération de l'ID du Timetable depuis l'URL
        timetable_id = self.kwargs.get('timetable_id')
        # Vous pouvez éventuellement pré-remplir d'autres champs si nécessaire
        return initial

    def form_valid(self, form):
        timetable_id = self.kwargs.get('timetable_id')
        timetable = get_object_or_404(Timetable, id=timetable_id)
        
        subject = form.cleaned_data['subject']
        teacher = form.cleaned_data['teacher']
        department_levels = form.cleaned_data['department_levels']
        room = form.cleaned_data['room']
        session_date = form.cleaned_data['session_date']
        timeslot = form.cleaned_data.get('timeslot')
        new_start_time = form.cleaned_data.get('new_start_time')
        new_end_time = form.cleaned_data.get('new_end_time')
        
        # Utilisation d'un créneau existant ou création d'un nouveau créneau
        if not timeslot:
            timeslot = TimeSlot.objects.create(
                start_time=new_start_time,
                end_time=new_end_time
            )
        
        with transaction.atomic():
            # Création de la session complémentaire
            CourseSession.objects.create(
                timetable=timetable,
                subject=subject,
                teacher=teacher,
                room=room,
                date=session_date,
                timeslot=timeslot,
            )
        
        # Si la date de la session est égale à la date de fin du Timetable, rediriger vers la liste des emplois du temps
        if session_date == timetable.end_date:
            return redirect(reverse_lazy('timetables:timetable_list'))
        else:
            # Sinon, rester dans la même vue pour ajouter d'autres sessions
            return redirect(reverse_lazy('coursesessions:add_more', kwargs={'timetable_id': timetable_id}))


class TimetableDeleteView(DeleteView):
    model = Timetable
    template_name = 'timetable/timetable_confirm_delete.html'
    success_url = reverse_lazy('timetables:list')
