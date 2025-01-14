from django.urls import path

from apps.rooms.views import RoomCreateView, RoomDeleteView, RoomListView, RoomUpdateView

app_name = 'rooms'

urlpatterns = [
    path('rooms/', RoomListView.as_view(), name='room_list'),
    path('rooms/create/', RoomCreateView.as_view(), name='room_create'),
    path('rooms/update/<int:pk>/', RoomUpdateView.as_view(), name='room_update'),
    path('rooms/delete/<int:pk>/', RoomDeleteView.as_view(), name='room_delete'),
    
    ]
