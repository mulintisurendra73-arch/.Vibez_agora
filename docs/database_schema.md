# Database schema — Phase 1

Phase 1 uses Django's built-in authentication tables, created by `python manage.py migrate`:

- `auth_user` (username, password hash, email, first name/display name, staff/superuser flags, active flag, timestamps via related auth tables as applicable)
- `auth_group`, `auth_permission`, `auth_user_groups`, `auth_user_user_permissions`
- `django_session` for server-side sessions
- `django_content_type`, `django_admin_log`, and migration bookkeeping tables

The registration form stores the display name in Django's `first_name` field to avoid introducing a custom user model before the first migration. A later phase can add a `Profile` model and should decide whether to retain or migrate this display name. Room, message, wallet, gift, follow, block, report, notification, badge, and level tables are not yet implemented.
