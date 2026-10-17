from django.urls import path
from . import views

urlpatterns = [
    path("discover/", views.discover_view, name="discover"),
    path("rooms/", views.rooms_view, name="rooms"),
    path("rooms/create/", views.create_room, name="create_room"),
    path("rooms/<int:room_id>/", views.room_detail, name="room_detail"),
    path("rooms/<int:room_id>/agora-token/", views.agora_token_view, name="agora_token"),
    path("rooms/<int:room_id>/join/", views.join_room, name="join_room"),
    path("rooms/<int:room_id>/leave/", views.leave_room, name="leave_room"),
    path("rooms/<int:room_id>/seats/<int:seat_number>/join/", views.join_seat, name="join_seat"),
    path("rooms/<int:room_id>/seats/leave/", views.leave_seat, name="leave_seat"),
    path("rooms/<int:room_id>/close/", views.close_room, name="close_room"),
    path("rooms/<int:room_id>/reopen/", views.reopen_room, name="reopen_room"),
    path("rooms/<int:room_id>/members/<int:user_id>/role/", views.set_member_role, name="set_member_role"),
    path("rooms/<int:room_id>/members/<int:user_id>/mute/", views.toggle_member_mute, name="toggle_member_mute"),
]
