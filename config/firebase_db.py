
import os
from pathlib import Path

import firebase_admin
from firebase_admin import credentials, db
from django.conf import settings

_app = None


def get_firebase_app():
    global _app

    if _app is not None:
        return _app

    project_root = Path(settings.BASE_DIR)
    credentials_path = os.getenv(
        "FIREBASE_CREDENTIALS_PATH",
        "secrets/firebase-service-account.json",
    )

    credentials_path = Path(credentials_path)
    if not credentials_path.is_absolute():
        credentials_path = project_root / credentials_path

    database_url = os.getenv("FIREBASE_DATABASE_URL")

    if not database_url:
        raise RuntimeError("FIREBASE_DATABASE_URL is missing from .env")

    if not credentials_path.is_file():
        raise RuntimeError(
            f"Firebase credentials file not found: {credentials_path}"
        )

    try:
        _app = firebase_admin.get_app()
    except ValueError:
        credential = credentials.Certificate(str(credentials_path))
        _app = firebase_admin.initialize_app(
            credential,
            {"databaseURL": database_url},
        )

    return _app


def firebase_reference(path="/"):
    get_firebase_app()
    return db.reference(path)
