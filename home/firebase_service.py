
from config.firebase_db import firebase_reference


def publish_room(room):
    """Publish a Django room's public information to Firebase."""
    room_data = {
        "id": room.pk,
        "title": room.title,
        "description": room.description,
        "topic": room.topic,
        "status": room.status,
        "host_id": room.host_id,
        "updated_at": room.updated_at.isoformat(),
    }

    firebase_reference(f"/rooms/{room.pk}").set(room_data)
    return room_data


def remove_room(room_id):
    """Remove a room from Firebase when it is deleted."""
    firebase_reference(f"/rooms/{room_id}").delete()


def get_firebase_rooms():
    """Return room records currently stored in Firebase."""
    return firebase_reference("/rooms").get() or {}
