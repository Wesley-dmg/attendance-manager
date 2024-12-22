from django.core.exceptions import PermissionDenied
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin

from apps.rooms.forms import ReservationForm, RoomForm
from apps.rooms.models import Reservation, Room

# Vue pour lister les rooms
@method_decorator(user_passes_test(lambda u: u.is_admin), name='dispatch')
class RoomListView(LoginRequiredMixin, ListView):
    model = Room
    template_name = 'rooms/room_list.html'
    context_object_name = 'rooms'
    extra_context = {
        'create_url': reverse_lazy('rooms:room_create'),
        'edit_url': 'rooms:room_update',
        'delete_url': 'rooms:room_delete',
    }

    def get_queryset(self):
        return Room.objects.all()

# Vue pour créer une nouvelle salle
@method_decorator(user_passes_test(lambda u: u.is_admin), name='dispatch')
class RoomCreateView(LoginRequiredMixin, CreateView):
    permission_required = 'rooms.add_room'  # Permettre uniquement aux utilisateurs ayant la permission d'ajouter
    model = Room
    form_class = RoomForm
    template_name = 'rooms/form.html'
    success_url = reverse_lazy('rooms:room_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _("Ajouter une salle")
        context['cancel_url'] = reverse_lazy('rooms:room_list')
        return context

# Vue pour mettre à jour une salle existante
@method_decorator(user_passes_test(lambda u: u.is_admin), name='dispatch')
class RoomUpdateView(LoginRequiredMixin,  UpdateView):
    permission_required = 'rooms.change_room'
    model = Room
    form_class = RoomForm
    template_name = 'rooms/form.html'
    success_url = reverse_lazy('rooms:room_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _("Modifier la salle : %s") % self.object.name
        context['cancel_url'] = reverse_lazy('rooms:room_list')
        return context

# Vue pour supprimer une salle
@method_decorator(user_passes_test(lambda u: u.is_admin), name='dispatch')
class RoomDeleteView(LoginRequiredMixin, DeleteView):
    permission_required = 'rooms.delete_room'
    model = Room
    template_name = 'rooms/confirm_delete.html'
    success_url = reverse_lazy('rooms:room_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object_name'] = self.object.name
        context['cancel_url'] = reverse_lazy('rooms:room_list')
        return context

# Vue pour lister les réservations
@method_decorator(user_passes_test(lambda u: u.is_admin), name='dispatch')
class ReservationListView(ListView):
    model = Reservation
    template_name = 'rooms/reservation_list.html'
    context_object_name = 'reservations'
    extra_context = {
        'create_url': reverse_lazy('rooms:reservation_create'),
        'edit_url': 'rooms:reservation_update',
        'delete_url': 'rooms:reservation_delete',
    }

    def get_queryset(self):
        return Reservation.objects.all()

# Vue pour créer une nouvelle réservation
@method_decorator(user_passes_test(lambda u: u.is_admin), name='dispatch')
class ReservationCreateView(LoginRequiredMixin, CreateView):
    model = Reservation
    form_class = ReservationForm
    template_name = 'rooms/form.html'
    success_url = reverse_lazy('rooms:reservation_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user  # Passer l'utilisateur connecté
        return kwargs

    def form_valid(self, form):
        form.instance.user = self.request.user  # Associer l’utilisateur connecté à la réservation
        if Reservation.objects.filter(
            room=form.cleaned_data['room'],
            reservation_date=form.cleaned_data['reservation_date'],
            start_time__lt=form.cleaned_data['end_time'],
            end_time__gt=form.cleaned_data['start_time']
        ).exists():
            form.add_error(None, _("La salle est déjà réservée pour ces horaires."))
            return self.form_invalid(form)
        
        # Marquer la salle comme indisponible
        form.instance.room.mark_as_unavailable()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _("Créer une réservation")
        context['cancel_url'] = reverse_lazy('rooms:reservation_list')
        return context

# Vue pour mettre à jour une réservation existante
@method_decorator(user_passes_test(lambda u: u.is_admin), name='dispatch')
class ReservationUpdateView(LoginRequiredMixin, UpdateView):
    model = Reservation
    form_class = ReservationForm
    template_name = 'rooms/form.html'
    success_url = reverse_lazy('rooms:reservation_list')

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if not self.request.user.is_admin and obj.user != self.request.user:
            raise PermissionDenied(_("Vous n'avez pas la permission de modifier cette réservation."))
        return obj

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        old_room = self.object.room
        new_room = form.cleaned_data['room']

        # Rendre la salle précédente disponible si elle change
        if old_room != new_room:
            old_room.mark_as_available()
            new_room.mark_as_unavailable()

        # Restriction pour les utilisateurs non admins
        if not self.request.user.is_admin:
            form.instance.user = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _("Modifier la réservation pour : %s") % self.object.room.name
        context['cancel_url'] = reverse_lazy('rooms:reservation_list')
        return context

# Vue pour supprimer une réservation
@method_decorator(user_passes_test(lambda u: u.is_admin), name='dispatch')
class ReservationDeleteView(LoginRequiredMixin, DeleteView):
    model = Reservation
    template_name = 'rooms/confirm_delete.html'
    success_url = reverse_lazy('rooms:reservation_list')

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if not self.request.user.is_admin and obj.user != self.request.user:
            raise PermissionDenied(_("Vous n'avez pas la permission de supprimer cette réservation."))
        return obj

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        room = self.object.room
        room.mark_as_available()  # Marquer la salle comme disponible
        self.object.delete()  # Supprimer la réservation
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object_name'] = f"{self.object.room.name} - {self.object.reservation_date}"
        context['cancel_url'] = reverse_lazy('rooms:reservation_list')
        return context
    
    