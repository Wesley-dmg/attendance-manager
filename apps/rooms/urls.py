from django.urls import path

from apps.rooms.views import RoomCreateView, RoomDeleteView, RoomListView, RoomUpdateView

app_name = 'rooms'

urlpatterns = [
    path('rooms/', RoomListView.as_view(), name='room_list'),
    path('rooms/create/', RoomCreateView.as_view(), name='room_create'),
    path('rooms/update/<int:pk>/', RoomUpdateView.as_view(), name='room_update'),
    path('rooms/delete/<int:pk>/', RoomDeleteView.as_view(), name='room_delete'),
    
    # path('reservations/', AdminReservationListView.as_view(), name='reservation_list'),
    # path('reservations/create/', ReservationCreateView.as_view(), name='reservation_create'),
    # path('reservations/update/<int:pk>/', ReservationUpdateView.as_view(), name='reservation_update'),
    # path('reservations/delete/<int:pk>/', ReservationDeleteView.as_view(), name='reservation_delete'),
    
    # path('reservation/validate/<int:pk>/', ReservationValidateView.as_view(), name='reservation_validate'),
    # path('reservation/reject/<int:pk>/', ReservationRejectView.as_view(), name='reservation_reject'),
]
