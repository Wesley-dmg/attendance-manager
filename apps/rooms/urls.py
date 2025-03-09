from django.urls import path

from apps.rooms.views import RoomCreateView, RoomDeleteView, RoomListView, RoomUpdateView

app_name = 'rooms'

urlpatterns = [
    path('', RoomListView.as_view(), name='room_list'),
    path('create/', RoomCreateView.as_view(), name='room_create'),
    path('update/<int:pk>/', RoomUpdateView.as_view(), name='room_update'),
    path('delete/<int:pk>/', RoomDeleteView.as_view(), name='room_delete'),
    
    ]
