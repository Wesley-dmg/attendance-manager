from django.contrib import admin
from django.contrib.auth.models import Permission
from django.utils.translation import gettext_lazy as _

from apps.rooms.models import Room

class RoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'available')
    search_fields = ('name', 'location')
    list_filter = ('available',)
    ordering = ('name',)
    
    # Méthode pour afficher la disponibilité d'une salle
    def get_room_status(self, obj):
        return _('Disponible') if obj.available else _('Indisponible')
    get_room_status.short_description = _('Statut de la salle')

# Enregistrer le modèle `Room` dans l'admin
admin.site.register(Room, RoomAdmin)

# class ReservationAdmin(admin.ModelAdmin):
#     list_display = ('room', 'user', 'reservation_date', 'start_time', 'end_time', 'validated')
#     search_fields = ('room__name', 'user__username')
#     list_filter = ('validated', 'reservation_date')
#     ordering = ('reservation_date', 'start_time')

#     def get_user_full_name(self, obj):
#         return obj.user.get_full_name()
#     get_user_full_name.short_description = _('Utilisateur')

# # Enregistrer le modèle `Reservation` dans l'admin
# admin.site.register(Reservation, ReservationAdmin)
