from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import user_passes_test,login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views import View
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.utils.decorators import method_decorator

from apps.home.utils import send_custom_message
from apps.rooms.forms import RoomForm
from apps.rooms.models import Room
from apps.home.mixins import AdminTestMixin

# Vue pour lister les salles
class RoomListView(LoginRequiredMixin,PermissionRequiredMixin,AdminTestMixin,ListView):
    model = Room
    template_name = 'rooms/room_list.html'
    permission_required= 'rooms.view_room'
    context_object_name = 'rooms'
    extra_context = {
        'title': 'Liste des Salles',
        'create_url': reverse_lazy('rooms:room_create'),
        'edit_url': 'rooms:room_update',
        'delete_url': 'rooms:room_delete',
    }

    def get_queryset(self):
        return Room.objects.all()

# Vue pour créer une nouvelle salle
class RoomCreateView(LoginRequiredMixin,PermissionRequiredMixin,AdminTestMixin,CreateView):
    model = Room
    form_class = RoomForm
    template_name = 'rooms/form.html'
    permission_required = 'rooms.add_room'  # Accès réservé aux utilisateurs autorisés
    success_url = reverse_lazy('rooms:room_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _("Ajouter une salle")
        context['cancel_url'] = reverse_lazy('rooms:room_list')
        return context

# Vue pour mettre à jour une salle existante
class RoomUpdateView(LoginRequiredMixin,PermissionRequiredMixin,AdminTestMixin,UpdateView):
    model = Room
    form_class = RoomForm
    template_name = 'rooms/form.html'
    permission_required = 'rooms.change_room'
    success_url = reverse_lazy('rooms:room_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Utilisation du champ 'room_number' pour afficher le titre de la salle
        context['title'] = _("Modifier la salle : %s") % self.object.room_number
        context['cancel_url'] = reverse_lazy('rooms:room_list')
        return context

# Vue pour supprimer une salle
class RoomDeleteView(LoginRequiredMixin,PermissionRequiredMixin,AdminTestMixin,DeleteView):
    model = Room
    template_name = 'rooms/confirm_delete.html'
    permission_required = 'rooms.delete_room'
    success_url = reverse_lazy('rooms:room_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Affichage du numéro de la salle pour confirmation
        context['object_name'] = self.object.room_number
        context['cancel_url'] = reverse_lazy('rooms:room_list')
        return context
