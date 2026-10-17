# .Vibez — Phase 1 setup guide

This milestone is a Django-rendered landing page with responsive navigation, registration, login/logout, Django password validation, and password-reset views. It uses SQLite locally. It is not yet a social network: rooms, messaging, profiles, gifts, WebSockets, and live audio are later phases.

## Requirements
- Python 3.10 or newer (Python 3.13 is supported by the Django 5.2 series)
- Visual Studio Code
- A terminal and a modern browser

## 1. Open the project
Open the `social_app` folder in VS Code. Open **Terminal → New Terminal**.

## 2. Create and activate a virtual environment
Windows PowerShell:
```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```
If PowerShell blocks activation, use Command Prompt instead:
```bat
.venv\Scripts\activate.bat
```
macOS/Linux:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

## 3. Install dependencies
```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 4. Check configuration and create the local database
```bash
python manage.py check
python manage.py migrate
```

## 5. Start the server
```bash
python manage.py runserver
```
Open http://127.0.0.1:8000/ in your browser. Registration is at http://127.0.0.1:8000/accounts/register/ and login is at http://127.0.0.1:8000/accounts/login/.

## 6. Test authentication
1. Create an account on the registration page.
2. Log in with your username and password.
3. The header should greet you with your display name.
4. Use **Sign out** to log out.
5. Run `python manage.py test` to execute the starter tests.

## Optional: administrator
Create an admin account with `python manage.py createsuperuser`, then visit http://127.0.0.1:8000/admin/. Phase 1 has only Django's built-in user/admin models registered by default.

## Password recovery note
The password-reset views exist, but email delivery is not configured. For local testing you can add Django's console email backend to `config/settings.py` (`EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"`) so reset emails print in the terminal. Do not use console email in production.

## Troubleshooting
- **`No module named django`**: activate `.venv`, then run `pip install -r requirements.txt`.
- **`python` not found on Windows**: use `py` for environment creation; after activation, `python` normally works.
- **PowerShell script execution blocked**: activate using Command Prompt or adjust your execution policy according to your device policy.
- **Port 8000 is busy**: run `python manage.py runserver 8001` and open http://127.0.0.1:8001/.
- **CSS changes do not appear**: hard refresh with Ctrl+F5 and confirm the `static/css/site.css` file is in place.
- **Password rejected**: Django checks common passwords, minimum length, numeric-only passwords, and similarity to account details.

## Security before deployment
Set a strong random `DJANGO_SECRET_KEY`, set `DJANGO_DEBUG=False`, configure `DJANGO_ALLOWED_HOSTS`, use HTTPS, configure secure cookies, set up email delivery, review upload policy, and run `python manage.py check --deploy`. Never deploy with the development secret or `DEBUG=True`.
