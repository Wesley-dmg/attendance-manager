from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from apps.rooms.models import Room, Building, Floor


class RoomAdmin(admin.ModelAdmin):
    list_display = ('room_number', 'building', 'floor', 'get_room_status')
    search_fields = ('room_number', 'building__name', 'floor__number')
    list_filter = ('available', 'building', 'floor')
    ordering = ('building', 'floor', 'room_number')

    def get_room_status(self, obj):
        """Affiche le statut de la salle en fonction de sa disponibilité."""
        return _('Disponible') if obj.available else _('Indisponible')
    
    get_room_status.short_description = _('Statut de la salle')


class BuildingAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)


class FloorAdmin(admin.ModelAdmin):
    list_display = ('number', 'building')
    search_fields = ('number', 'building__name')
    list_filter = ('building',)
    ordering = ('building', 'number')


# Enregistrement des modèles dans l'admin
admin.site.register(Room, RoomAdmin)
admin.site.register(Building, BuildingAdmin)
admin.site.register(Floor, FloorAdmin)
