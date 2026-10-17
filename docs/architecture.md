# Architecture — Phase 1

- **Presentation:** Django templates in `templates/`; responsive styles in `static/css/site.css`; small progressive-enhancement script in `static/js/site.js`.
- **Application:** `config` owns project settings and URL routing. `home` renders the landing page. `accounts` owns the registration form and registration view.
- **Authentication:** Django's built-in auth framework, session middleware, password hashing, login/logout views, and password validators.
- **Database:** SQLite at `db.sqlite3` for local development; schema is managed by Django migrations.
- **ASGI/WSGI:** entry points are configured for future deployment and Channels integration, but Channels is not installed or enabled in Phase 1.

## Deliberate Phase 1 boundaries
The sample cards on the landing page are explicitly illustrative and are not database-backed rooms. There is no WebSocket, live audio, messaging, coin wallet, gifts, OTP provider, push provider, or Flutter client yet. Those are later milestones and should be added with tests and incremental migrations.
