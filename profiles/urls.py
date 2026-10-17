from django.urls import path
from . import views

urlpatterns = [
    path("me/", views.my_profile, name="my_profile"),
    path("me/edit/", views.edit_profile, name="edit_profile"),
    path("notifications/", views.notifications_view, name="notifications"),
    path("<str:username>/follow/", views.toggle_follow, name="toggle_follow"),
    path("<str:username>/block/", views.toggle_block, name="toggle_block"),
    path("<str:username>/report/", views.report_user, name="report_user"),
    path("<str:username>/", views.public_profile, name="public_profile"),
]
