import json
import ssl
import os
import tempfile
import unittest
import urllib.parse
from unittest.mock import patch

from pendo_backend import BackendError, PendoBackend


class PendoBackendTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.config_path = os.path.join(self.temp_dir.name, "backend_config.json")

    def write_config(self, **values):
        with open(self.config_path, "w", encoding="utf-8") as handle:
            json.dump(values, handle)

    def test_config_requires_https_url_and_public_key(self):
        self.write_config(supabase_url="http://example.supabase.co", supabase_anon_key="public")
        backend = PendoBackend(self.config_path)
        self.assertFalse(backend.configured)

        self.write_config(supabase_url="https://example.supabase.co", supabase_anon_key="public")
        backend = PendoBackend(self.config_path)
        self.assertTrue(backend.configured)

    def test_signup_passes_encoded_redirect_url(self):
        callback = PendoBackend.AUTH_CALLBACK_URL
        self.write_config(
            supabase_url="https://example.supabase.co",
            supabase_anon_key="public",
            auth_redirect_url=callback,
        )
        backend = PendoBackend(self.config_path)

        with patch.object(backend, "_request", return_value={}) as request:
            backend.sign_up("person@example.com", "correct-horse-battery")
        args, kwargs = request.call_args
        self.assertEqual(args[0], "/auth/v1/signup?redirect_to=" + urllib.parse.quote(callback, safe=""))
        self.assertEqual(args[1], "POST")
        self.assertEqual(args[2], {"email": "person@example.com", "password": "correct-horse-battery"})

    def test_empty_redirect_config_uses_native_pendo_callback(self):
        self.write_config(supabase_url="https://example.supabase.co", supabase_anon_key="public")
        backend = PendoBackend(self.config_path)

        with patch.object(backend, "_request", return_value={}) as request:
            backend.sign_up("person@example.com", "correct-horse-battery")
        self.assertEqual(request.call_args.args[0], "/auth/v1/signup?redirect_to=com.pendo.app.pendo%3A%2F%2Fauth-callback")

    def test_password_recovery_uses_same_redirect(self):
        callback = PendoBackend.AUTH_CALLBACK_URL
        self.write_config(
            supabase_url="https://example.supabase.co",
            supabase_anon_key="public",
            auth_redirect_url=callback,
        )
        backend = PendoBackend(self.config_path)

        with patch.object(backend, "_request", return_value=None) as request:
            backend.reset_password("person@example.com")
        self.assertEqual(
            request.call_args.args[0],
            "/auth/v1/recover?redirect_to=com.pendo.app.pendo%3A%2F%2Fauth-callback",
        )

    def test_auth_callback_accepts_session_fragment(self):
        self.write_config(supabase_url="https://example.supabase.co", supabase_anon_key="public")
        backend = PendoBackend(self.config_path)
        callback = PendoBackend.AUTH_CALLBACK_URL + "#access_token=access&refresh_token=refresh&type=signup"
        with patch.object(backend, "_request", return_value={"id": "user-1", "email": "person@example.com"}):
            result = backend.complete_auth_callback(callback)
        self.assertEqual(result["type"], "signup")
        self.assertEqual(result["user"]["id"], "user-1")
        self.assertEqual(backend.access_token, "access")
        self.assertEqual(backend.refresh_token, "refresh")

    def test_auth_callback_rejects_wrong_scheme_or_host(self):
        self.write_config(supabase_url="https://example.supabase.co", supabase_anon_key="public")
        backend = PendoBackend(self.config_path)
        with self.assertRaises(BackendError):
            backend.complete_auth_callback("https://example.com/#access_token=x")

    def test_auth_callback_surfaces_supabase_error(self):
        self.write_config(supabase_url="https://example.supabase.co", supabase_anon_key="public")
        backend = PendoBackend(self.config_path)
        callback = PendoBackend.AUTH_CALLBACK_URL + "#error=access_denied&error_description=Email+link+expired"
        with self.assertRaisesRegex(BackendError, "Email link expired"):
            backend.complete_auth_callback(callback)

    def test_update_password_requires_session_and_minimum_length(self):
        self.write_config(supabase_url="https://example.supabase.co", supabase_anon_key="public")
        backend = PendoBackend(self.config_path)
        with self.assertRaises(BackendError):
            backend.update_password("short")
        backend.access_token = "access"
        with patch.object(backend, "_request", return_value={"id": "user-1"}) as request:
            backend.update_password("a-secure-password")
        self.assertEqual(request.call_args.args[0], "/auth/v1/user")
        self.assertEqual(request.call_args.args[1], "PUT")

    def test_sign_in_stores_session(self):
        self.write_config(supabase_url="https://example.supabase.co", supabase_anon_key="public")
        backend = PendoBackend(self.config_path)
        session = {
            "access_token": "access",
            "refresh_token": "refresh",
            "user": {"id": "user-1", "email": "person@example.com"},
        }
        with patch.object(backend, "_request", return_value=session):
            user = backend.sign_in("person@example.com", "password")
        self.assertEqual(user["id"], "user-1")
        self.assertEqual(backend.access_token, "access")
        self.assertEqual(backend.refresh_token, "refresh")

    def test_sign_in_rejects_empty_response(self):
        self.write_config(supabase_url="https://example.supabase.co", supabase_anon_key="public")
        backend = PendoBackend(self.config_path)
        with patch.object(backend, "_request", return_value=None):
            with self.assertRaises(BackendError):
                backend.sign_in("person@example.com", "password")


    def test_malformed_json_object_does_not_crash_config_loading(self):
        with open(self.config_path, "w", encoding="utf-8") as handle:
            json.dump(["not", "an", "object"], handle)
        backend = PendoBackend(self.config_path)
        self.assertFalse(backend.configured)

    def test_ssl_context_keeps_certificate_verification_enabled(self):
        with patch("pendo_backend.certifi", None):
            context = PendoBackend._ssl_context()
        self.assertEqual(context.verify_mode, ssl.CERT_REQUIRED)
        self.assertTrue(context.check_hostname)


if __name__ == "__main__":
    unittest.main()
