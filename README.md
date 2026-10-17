# .Vibez — Phase 1

Beginner-friendly Django starter for a social-audio community concept. This milestone includes a responsive landing page, registration, login/logout, Django password validation, and password-reset views. It does not yet include live rooms, messaging, gifts, WebSockets, or real audio.

## Quick start (Windows PowerShell)
```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python manage.py check
python manage.py migrate
python manage.py runserver
```
Open http://127.0.0.1:8000/.

See `docs/setup_guide.md` for Command Prompt/macOS/Linux instructions, testing, troubleshooting, and deployment cautions.


## Phase 2

See `docs/phase2_guide.md` for profile pages, profile editing, follow/unfollow, migrations, and tests.


## Phase 3: .Vibez discovery and rooms
See `docs/phase3_guide.md` for migration and run instructions. The visible product name is now `.Vibez`.

## Phase 4: Privacy and safety
See `docs/phase4_guide.md` for profile privacy, blocking, reporting, notifications, migrations, and testing steps.


## Live audio with Agora (RTC)

1. Create an Agora project in the Agora Console and enable RTC. Use an App ID and App Certificate from the same project.
2. Copy `.env.example` to `.env` and set `AGORA_APP_ID` and `AGORA_APP_CERTIFICATE`. Do not commit `.env` or expose the certificate in browser code.
3. Install dependencies and run the app:
   ```powershell
   pip install -r requirements.txt
   python manage.py check
   python manage.py migrate
   python manage.py runserver
   ```
4. Log in, join an open room, and press **Join audio**. Listeners subscribe to room audio. A user needs an available talking seat to publish microphone audio. Host mute state is checked periodically by the page.

The browser SDK is loaded from Agora's CDN, so clients need internet access. Microphone access requires localhost or HTTPS. Agora credentials are required; placeholder values do not connect. The current implementation uses numeric Django user IDs as Agora UIDs and short-lived RTC tokens. For production, add rate limiting, HTTPS, secure secret management, and a robust mechanism to revoke speaker publishing immediately when a host mutes a user.
