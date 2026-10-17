# .Vibez Phase 5 — Room management

Adds host-only close/reopen controls, room capacity, a room member list, and app-level speaker/listener and mute flags. These flags do **not** mute a microphone or transmit audio; real-time voice requires the later audio phase.

## Update an existing Phase 4 checkout
1. Back up the project and `db.sqlite3`.
2. Copy updated source files into the existing project, preserving the database and existing migration files.
3. Activate the virtual environment and run `python manage.py check`.
4. Run `python manage.py makemigrations home` and inspect the generated migration.
5. Run `python manage.py migrate`.
6. Run `python manage.py test`.

If you extracted this as a separate folder, copy your existing `db.sqlite3` and migration history only if you understand that they belong to the same project. Do not delete or flush the database.
