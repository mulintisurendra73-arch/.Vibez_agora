from django.contrib import admin
from .models import Profile, Follow, Block, UserReport, Notification

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "is_private", "created_at", "updated_at")
    list_filter = ("is_private",)
    search_fields = ("user__username", "user__email", "bio")

@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ("follower", "followed", "created_at")
    search_fields = ("follower__username", "followed__username")

@admin.register(Block)
class BlockAdmin(admin.ModelAdmin):
    list_display = ("blocker", "blocked", "created_at")
    search_fields = ("blocker__username", "blocked__username")

@admin.register(UserReport)
class UserReportAdmin(admin.ModelAdmin):
    list_display = ("reporter", "reported_user", "reason", "reviewed", "created_at")
    list_filter = ("reason", "reviewed", "created_at")
    search_fields = ("reporter__username", "reported_user__username", "details")
    list_editable = ("reviewed",)

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("recipient", "actor", "kind", "is_read", "created_at")
    list_filter = ("kind", "is_read", "created_at")
    search_fields = ("recipient__username", "actor__username", "message")
