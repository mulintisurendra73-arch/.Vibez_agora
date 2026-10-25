
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from profiles.cloudinary_storage import ProfileImageStorage


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    bio = models.CharField(max_length=280, blank=True)
    is_private = models.BooleanField(
        default=False,
        help_text="Only approved followers can view your full profile.",
    )
    avatar = models.ImageField(
        storage=ProfileImageStorage(),
        upload_to="profiles/",
        blank=True,
        null=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile for {self.user.username}"

    @property
    def follower_count(self):
        return self.user.followers.count()

    @property
    def following_count(self):
        return self.user.following.count()


class Follow(models.Model):
    follower = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="following",
    )
    followed = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="followers",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("follower", "followed"),
                name="unique_user_follow",
            )
        ]
        indexes = [
            models.Index(fields=("followed", "created_at")),
            models.Index(fields=("follower", "created_at")),
        ]

    def clean(self):
        if self.follower_id == self.followed_id:
            raise ValidationError("You cannot follow yourself.")

    def save(self, *args, **kwargs):
        self.clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.follower} follows {self.followed}"


class Block(models.Model):
    blocker = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="blocked_users",
    )
    blocked = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="blocked_by_users",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("blocker", "blocked"),
                name="unique_user_block",
            )
        ]

    def clean(self):
        if self.blocker_id == self.blocked_id:
            raise ValidationError("You cannot block yourself.")

    def save(self, *args, **kwargs):
        self.clean()
        result = super().save(*args, **kwargs)

        Follow.objects.filter(
            follower_id=self.blocker_id,
            followed_id=self.blocked_id,
        ).delete()

        Follow.objects.filter(
            follower_id=self.blocked_id,
            followed_id=self.blocker_id,
        ).delete()

        return result

    def __str__(self):
        return f"{self.blocker} blocked {self.blocked}"


class UserReport(models.Model):
    class Reason(models.TextChoices):
        SPAM = "spam", "Spam"
        HARASSMENT = "harassment", "Harassment or bullying"
        INAPPROPRIATE = "inappropriate", "Inappropriate content"
        IMPERSONATION = "impersonation", "Impersonation"
        OTHER = "other", "Other"

    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="submitted_reports",
    )
    reported_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="received_reports",
    )
    reason = models.CharField(max_length=24, choices=Reason.choices)
    details = models.CharField(max_length=1000, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed = models.BooleanField(default=False)

    def __str__(self):
        return (
            f"Report by {self.reporter} about "
            f"{self.reported_user} ({self.reason})"
        )


class Notification(models.Model):
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications_sent",
    )
    kind = models.CharField(max_length=40)
    message = models.CharField(max_length=200)
    target_url = models.CharField(max_length=300, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"Notification for {self.recipient}: {self.message}"
