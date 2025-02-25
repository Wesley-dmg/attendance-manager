from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.views import View
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin

from apps.home.utils import send_custom_message
from apps.rooms.forms import RoomForm
from apps.rooms.models import Room

# Vue pour lister les salles
@method_decorator([login_required, user_passes_test(lambda u: u.is_admin)], name='dispatch')
class RoomListView(ListView):
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
@method_decorator([login_required, user_passes_test(lambda u: u.is_admin)], name='dispatch')
class RoomCreateView(CreateView):
    permission_required = 'rooms.add_room'  # Accès réservé aux utilisateurs autorisés
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
@method_decorator([login_required, user_passes_test(lambda u: u.is_admin)], name='dispatch')
class RoomUpdateView(UpdateView):
    permission_required = 'rooms.change_room'
    model = Room
    form_class = RoomForm
    template_name = 'rooms/form.html'
    success_url = reverse_lazy('rooms:room_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Utilisation du champ 'room_number' pour afficher le titre de la salle
        context['title'] = _("Modifier la salle : %s") % self.object.room_number
        context['cancel_url'] = reverse_lazy('rooms:room_list')
        return context

# Vue pour supprimer une salle
@method_decorator([login_required, user_passes_test(lambda u: u.is_admin)], name='dispatch')
class RoomDeleteView(DeleteView):
    permission_required = 'rooms.delete_room'
    model = Room
    template_name = 'rooms/confirm_delete.html'
    success_url = reverse_lazy('rooms:room_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Affichage du numéro de la salle pour confirmation
        context['object_name'] = self.object.room_number
        context['cancel_url'] = reverse_lazy('rooms:room_list')
        return context
