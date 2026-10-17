# .Vibez Phase 4 — Privacy, Safety and Notifications

## Included
- Private-profile toggle in Edit Profile. A private profile's bio and follower/following details are hidden from non-followers.
- Block and unblock actions. Creating a block removes follow relationships in both directions and prevents new follows between the two accounts.
- Report-user form with reason and optional details. Reports are saved for moderator review in Django Admin; this does not automatically suspend users.
- Follow notifications and a Notifications page. Opening the page marks notifications as read.
- Discover excludes accounts blocked by or blocking the signed-in user.
- Django Admin screens for profiles, blocks, reports, follows, and notifications.

## Upgrade an existing Phase 3 project
1. Back up the whole project folder and `db.sqlite3`.
2. Copy the Phase 4 files over your existing project, keeping your existing `db.sqlite3` and migration files.
3. Activate your virtual environment.
4. Run `python manage.py check`.
5. Run `python manage.py makemigrations profiles` (and `home` only if Django says home models changed).
6. Run `python manage.py migrate`.
7. Run `python manage.py test`.
8. Start the app with `python manage.py runserver`.

If installing into a completely separate extracted folder without existing migration files, run `python manage.py makemigrations accounts home profiles` before `python manage.py migrate`.

## Routes
- `/profiles/me/edit/` — edit profile and privacy setting
- `/profiles/<username>/` — public/private profile
- `/profiles/<username>/block/` — POST action to block/unblock
- `/profiles/<username>/report/` — POST action to report
- `/profiles/notifications/` — notifications

## Safety notes
This is a local-development milestone, not a full moderation or privacy compliance system. Reports require manual review by staff. Configure production HTTPS, secure secrets, media upload validation/storage, rate limits, moderation procedures, and appropriate privacy/legal notices before deployment. Real-time push notifications are not included; notifications are database-backed and shown on the page.
