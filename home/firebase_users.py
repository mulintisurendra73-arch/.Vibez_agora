
from django.contrib.auth import get_user_model
from django.utils import timezone

from config.firebase_db import firebase_reference


def publish_user(user):
    """Publish safe profile fields for a Django user to Firebase."""
    if not user or not user.pk:
        raise ValueError("A saved Django user is required.")

    display_name = (
        user.get_full_name().strip()
        if hasattr(user, "get_full_name")
        else ""
    )

    profile = {
        "user_id": str(user.pk),
        "username": user.get_username(),
        "display_name": display_name or user.get_username(),
        "updated_at": timezone.now().isoformat(),
    }

    firebase_reference(f"users/{user.pk}").update(profile)


def get_firebase_user(user_id):
    """Return a user's Firebase profile, if it exists."""
    return firebase_reference(f"users/{user_id}").get()


def delete_firebase_user(user_id):
    """Delete a user's Firebase profile."""
    firebase_reference(f"users/{user_id}").delete()
