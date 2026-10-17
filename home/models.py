from django.conf import settings
from django.db import models


class Room(models.Model):
    class Status(models.TextChoices):
        OPEN = "open", "Open"
        CLOSED = "closed", "Closed"

    host = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="hosted_rooms")
    title = models.CharField(max_length=80)
    description = models.CharField(max_length=240, blank=True)
    topic = models.CharField(max_length=40, blank=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.OPEN)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    @property
    def listener_count(self):
        return self.memberships.count()


class RoomMembership(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="memberships")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="room_memberships")
   
    class Role(models.TextChoices):
        HOST = "host", "Host"
        SPEAKER = "speaker", "Speaker"
        LISTENER = "listener", "Listener"

    joined_at = models.DateTimeField(auto_now_add=True)
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.LISTENER)
    is_muted = models.BooleanField(default=False)
    seat_number = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=("room", "user"), name="unique_room_membership"),
            models.UniqueConstraint(
                fields=("room", "seat_number"),
                condition=models.Q(seat_number__isnull=False),
                name="unique_room_seat",
            ),
        ]

    def __str__(self):
        return f"{self.user} in {self.room}"
