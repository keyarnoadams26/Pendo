# Pendo Mobile — starter

Mobile-first Kivy Android application prototype. Includes login/onboarding, tier-selection wall, home dashboard, and navigable module screens for tasks, calendar, bills, lists, documents, goals, settings, and a demo owner dashboard.

## Important
- Authentication, cloud sync, payments, ads, and push notifications are NOT connected.
- Tier selection is demo-only.
- Owner dashboard figures are placeholder data.
- Python is the mobile UI/app layer. `cpp/` contains a starter native C++ helper and is not currently compiled/linked into the Android app.
- This is a development prototype, not a production-ready app.

## Android build (Linux/Ubuntu or cloud build runner)
1. Install Buildozer and Android build dependencies (see Buildozer docs).
2. In this project folder run: `buildozer android debug`
3. APK output is in `bin/`.

## GitHub
Create a repository, upload/commit the project, then use the Android workflow in `.github/workflows/android.yml` (workflow starter) to build APK artifacts.

## Backend foundation (Supabase)

This iteration adds a REST/Auth client using Python's standard library, so it does not add a third-party networking dependency to the Android build. The login and account-creation screens use Supabase Auth when the backend is configured; otherwise login remains demo-only. Newly added module entries are submitted to Supabase when signed in.

### Configure Supabase
1. Create a Supabase project.
2. In **Project Settings → API**, copy the Project URL and the public `anon` key (never the `service_role` key).
3. Put these values in `backend_config.json`:
   - `supabase_url`: your project URL, e.g. `https://YOUR-PROJECT.supabase.co`
   - `supabase_anon_key`: the public anon key
4. Open the Supabase **SQL Editor**, paste `supabase_schema.sql`, and run it. The script creates profile and app-record tables, row-level security, and an auth-user profile trigger.
5. For testing, configure Authentication email-confirmation settings as appropriate. With email confirmation enabled, the app displays a confirmation message after signup.

### Security notes / current limits
- Only the public anon key belongs in the mobile app. Never embed a Supabase service-role key.
- SQL policies restrict profiles and records to the authenticated owner; a trigger prevents clients from changing subscription entitlements.
- Auth calls are made on background threads so the UI is not blocked.
- Session tokens are currently kept in memory only; persistent secure token storage and refresh handling are not implemented yet.
- This is a backend foundation, not a production release: record loading/editing/deletion, offline sync, payment verification, and admin roles are still pending.
- Keep `backend_config.json` with the public anon key only; it is not a secret, but do not commit any private service keys.
