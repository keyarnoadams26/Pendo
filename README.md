# Pendo Mobile

Pendo is a mobile-first personal organisation app built with Python and Kivy for Android, with Supabase used for authentication and cloud records.

## Current app screens

The current mobile UI has been redesigned around a consistent navy-and-blue visual system, card-based dashboard, persistent bottom navigation, section shortcuts and horizontal swipe navigation between primary areas. The visual layer is in `pendo_ui.kv`; the app remains a Kivy Android application.

- Sign-in and account creation entry point
- Plan selection / paywall presentation (Free, Plus, Premium)
- Home dashboard and section shortcuts
- Tasks and reminders
- Calendar entries
- Bills and subscriptions
- Lists
- Documents
- Goals and habits
- Settings and account
- Owner dashboard preview (demo only)

The redesigned module screens currently support adding and viewing simple text records. They are still a foundation rather than complete task, calendar, bill, document or goal-management systems. The bottom navigation and horizontal swipe gestures move between Home, Explore and Account; a right-swipe from a module returns Home.

## Backend setup

The app uses `pendo_backend.py`, a small Supabase REST/Auth client.

1. Create a Supabase project.
2. In **Project Settings → API**, copy the Project URL and public anon/publishable key.
3. Put them in `backend_config.json` as `supabase_url` and `supabase_anon_key`.
4. Pendo uses the Android callback `com.pendo.app.pendo://auth-callback`. It is registered in the Android manifest and used for signup confirmation and password recovery.
5. In **Authentication → URL Configuration**, add `com.pendo.app.pendo://auth-callback` to **Redirect URLs** and set **Site URL** to the same callback. Supabase supports custom mobile deep-link URLs for this purpose. The app handles the returned session and displays a password-update prompt for recovery links. Keep **Site URL** as a valid HTTPS website URL; put the custom app scheme only in **Redirect URLs**.
6. Run `supabase_schema.sql` in the Supabase SQL Editor.

Only the public anon key belongs in the mobile app. Never include a Supabase service-role key in the repository or APK.

## Google sign-in setup

Pendo opens Supabase's hosted OAuth endpoint in the device browser and requests Google sign-in. The Android callback is the same registered deep link used by email confirmation.

Before Google sign-in can work, enable **Google** under **Supabase → Authentication → Providers**, add the Google OAuth client ID and client secret from a Google Cloud OAuth client, and configure the Supabase callback URL shown in the Supabase provider setup instructions. Also allow `com.pendo.app.pendo://auth-callback` under **Authentication → URL Configuration → Redirect URLs**. Google provider credentials and provider setup cannot be completed by changing the app repository alone.

## Subscription and payment status

The plan-selection screen currently records a selected plan in the user profile. It does **not** charge a customer, create a verified subscription, or process recurring payments.

**Planned South African payment provider: PayFast.** PayFast documents recurring subscriptions and custom API integration, making it a sensible first provider to evaluate for Pendo's monthly Plus and Premium plans. This is a design decision only: no PayFast account, credentials, checkout, or live payments are connected yet. Confirm merchant eligibility, fees, settlement rules and recurring-billing terms with PayFast before launch. See the [PayFast recurring billing overview](https://support.payfast.help/portal/en/kb/articles/can-i-receive-recurring-payments-20-9-2022) and [developer documentation](https://developers.payfast.co.za/docs#recurring_billing).

The eventual integration must create checkout sessions on a trusted server, validate payment notifications and signatures server-side, store subscription state in the database, and only then grant paid entitlements. Never put merchant secrets or a Supabase service-role key in the Android app. A responsible adult/business owner must handle merchant registration, contracts and payment-account administration.

## Android build

The GitHub Actions workflow is in `.github/workflows/main.yml`.

- Pushes to `main` run Python syntax validation and an Android debug APK build.
- Pull requests to `main` run Python syntax validation.
- You can also start a build manually from **GitHub → Actions → Build Pendo Android APK → Run workflow**.

The APK is uploaded as the `Pendo-Android-APK` workflow artifact when the build succeeds.

## Development status and production work still required

This is an active prototype, not a production release. Before release, complete and test:

- Secure session persistence, refresh-token handling and sign-out
- Physical-device testing of email confirmation and password-reset deep links on Android
- Feature-specific data models, editing, deletion, validation and search
- Offline handling, sync conflict handling and loading/error/empty states
- Verified payment checkout, recurring billing, webhooks and entitlement enforcement
- Account deletion, privacy controls, accessibility and device testing
- Server-side admin roles and real analytics (the owner dashboard is currently a demo)
- Automated tests and a release signing process

## Local build

On a supported Linux environment with Buildozer and Android build dependencies installed:

```bash
python -m compileall -q .
buildozer android debug
```
