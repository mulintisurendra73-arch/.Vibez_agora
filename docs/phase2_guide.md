# .Vibez Phase 2: Profiles and follows

## What's added
- Profile records automatically created when Django users are created.
- Profile page with follower/following counts and bio.
- Authenticated profile editing (display name, email, bio, optional avatar).
- Follow/unfollow via POST requests with CSRF protection.
- A unique database constraint prevents duplicate follow relationships.
- Django Admin registrations for profiles and follow relationships.

## Setup on Windows (from the project folder)
Activate your existing virtual environment, then run:

```powershell
pip install -r requirements.txt
python manage.py check
python manage.py makemigrations profiles
python manage.py migrate
python manage.py test
python manage.py runserver
```

Open `http://127.0.0.1:8000/profiles/me/` after logging in. Edit your profile at `/profiles/me/edit/`. Another user's public profile is `/profiles/<username>/`.

## Notes
- If an earlier database already exists, migrations preserve existing user records.
- Avatar upload support requires Pillow (included in requirements). For production, add strict upload-size limits, image processing, and private/secure object storage as needed.
- Email uniqueness is enforced by the registration and profile-edit forms. If you later need database-level case-insensitive uniqueness across all account creation paths, add a database constraint appropriate for the production database.
- Password recovery currently uses Django's development email backend unless email settings are configured; it does not deliver real email by default.
