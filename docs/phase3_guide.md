# .Vibez Phase 3 setup

This phase adds user discovery/search and database-backed rooms. It does not add real-time audio yet.

From the folder containing `manage.py`, activate your virtual environment and run:

```powershell
python manage.py check
python manage.py makemigrations home
python manage.py migrate
python manage.py test
python manage.py runserver
```

Routes: `/discover/`, `/rooms/`, `/rooms/create/`, and `/rooms/<id>/`. Creating and joining rooms requires login. Room join/leave actions use POST and CSRF protection.

The app name and visible branding have been changed to `.Vibez`. Existing database users and profile data are retained if you apply migrations to the existing database. Back up `db.sqlite3` before replacing source files.

Room membership is only a database presence count in this phase; voice chat and live listener synchronization are not implemented yet.
