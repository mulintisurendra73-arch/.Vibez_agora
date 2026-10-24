
from django.contrib.auth import get_user_model
from django.utils import timezone

from config.firebase_db import firebase_reference



def publish_user(user):
    """Publish safe profile fields for a Django user to Firebase."""
    if not user or not user.pk:
        raise ValueError("A saved Django user is required.")

    display_name = user.get_full_name().strip() or user.get_username()

    profile = {
        "user_id": str(user.pk),
        "username": user.get_username(),
        "display_name": display_name,
        "updated_at": timezone.now().isoformat(),
    }

    # Include profile details when a Profile record exists.
    try:
        user_profile = user.profile
        profile["bio"] = user_profile.bio or ""

        # Store the media URL, not the image file itself.
        if user_profile.avatar:
            profile["avatar_url"] = user_profile.avatar.url
        else:
            profile["avatar_url"] = ""
    except user._meta.model.DoesNotExist:
        profile["bio"] = ""
        profile["avatar_url"] = ""

    firebase_reference(f"users/{user.pk}").update(profile)



def get_firebase_user(user_id):
    """Return a user's Firebase profile, if it exists."""
    return firebase_reference(f"users/{user_id}").get()


def delete_firebase_user(user_id):
    """Delete a user's Firebase profile."""
    firebase_reference(f"users/{user_id}").delete()
