from django.contrib import admin
from .models import Room, RoomMembership

class RoomMembershipInline(admin.TabularInline):
    model = RoomMembership
    extra = 0

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ("title", "host", "topic", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("title", "description", "host__username")
    inlines = [RoomMembershipInline]

@admin.register(RoomMembership)
class RoomMembershipAdmin(admin.ModelAdmin):
    list_display = ("room", "user", "role", "is_muted", "joined_at")
    search_fields = ("room__title", "user__username")
