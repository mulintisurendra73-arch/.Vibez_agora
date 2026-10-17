# .Vibez Phase 6 — Eight Talking Seats & Unlimited Listeners

## Included
- Eight numbered seats on each room page.
- Authenticated users can join an available seat or leave their seat.
- Each seat can be occupied by only one member at a time (database constraint).
- Host can invite a room member to an available seat or move a seated member back to listeners.
- Listener capacity field and its form control are removed. Rooms no longer reject users after 50 members.
- Responsive seat grid for desktop and mobile.
- Added tests for seat rendering, seat join/leave, and duplicate-seat protection.

## Apply the update to your existing Windows project

1. Back up your existing `social_app` folder and `db.sqlite3`.
2. Copy the updated project files into your project, or use this project folder as your replacement.
3. Activate your virtual environment in VS Code.
4. Run:

   ```powershell
   python manage.py migrate
   python manage.py check
   python manage.py test
   ```
5. Start the server:

   ```powershell
   python manage.py runserver
   ```

6. Open `http://127.0.0.1:8000/`, log in, open a room, and test the eight seats.

## Important audio note
This phase implements the eight-seat assignment and unlimited-listener room-management behavior. It does **not** yet transmit microphone audio. The page states this explicitly. Live audio requires a separate WebRTC-compatible audio service and client integration; seat assignments alone do not create voice transmission.

## Database note
Migration `0004_unlimited_listeners_unique_seats.py` removes the `Room.max_listeners` field and adds a conditional uniqueness constraint so two memberships cannot occupy the same non-empty seat. Run `python manage.py migrate` before testing.
