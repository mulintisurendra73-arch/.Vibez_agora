
from django.utils import timezone
from django.conf import settings

from config.firebase_db import firebase_reference


def publish_user(user):
    """Publish safe profile fields for a Django user to Firebase."""
    if not user or not user.pk:
        raise ValueError("A saved Django user is required.")

    display_name = (
        user.get_full_name().strip()
        or user.get_username()
    )

    profile = {
        "user_id": str(user.pk),
        "username": user.get_username(),
        "display_name": display_name,
        "updated_at": timezone.now().isoformat(),
        "bio": "",
        "avatar_url": "",
    }

    try:
        user_profile = user.profile
        profile["bio"] = user_profile.bio or ""

        if user_profile.avatar:
            # Build an absolute URL using the current request-independent
            # site URL configured for this deployment.
            avatar_path = user_profile.avatar.url
            site_url = getattr(settings, "SITE_URL", "").rstrip("/")

            if avatar_path.startswith(("http://", "https://")):
                profile["avatar_url"] = avatar_path
            elif site_url:
                profile["avatar_url"] = f"{site_url}{avatar_path}"

    except user._meta.model.DoesNotExist:
        pass

    firebase_reference(f"users/{user.pk}").update(profile)


def get_firebase_user(user_id):
    """Return a user's Firebase profile, if it exists."""
    return firebase_reference(f"users/{user_id}").get()


def delete_firebase_user(user_id):
    """Delete a user's Firebase profile."""
    firebase_reference(f"users/{user_id}").delete()
