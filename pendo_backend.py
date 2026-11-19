"""Small Supabase REST/Auth client for Pendo; uses Python stdlib only."""
from __future__ import annotations
import json
import os
import urllib.error
import urllib.request
import urllib.parse
import socket
import ssl
try:
    import certifi
except ImportError:  # System CA store remains a secure fallback.
    certifi = None


class BackendError(Exception):
    pass


class PendoBackend:
    AUTH_CALLBACK_URL = "com.pendo.app.pendo://auth-callback"

    def __init__(self, config_path: str):
        self.config_path = config_path
        self.url = ""
        self.anon_key = ""
        self.access_token = None
        self.refresh_token = None
        self.user = None
        self._load_config()

    def _load_config(self):
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                cfg = json.load(f)
            if not isinstance(cfg, dict):
                raise ValueError("Backend configuration must be a JSON object.")
            self.url = str(cfg.get("supabase_url", "") or "").strip().rstrip("/")
            self.anon_key = str(cfg.get("supabase_anon_key", "") or "").strip()
        except (OSError, ValueError, TypeError):
            self.url, self.anon_key = "", ""

    @property
    def configured(self):
        try:
            parsed = urllib.parse.urlsplit(self.url)
            valid_url = parsed.scheme == "https" and bool(parsed.netloc) and not parsed.username and not parsed.password
        except ValueError:
            valid_url = False
        return bool(valid_url and self.anon_key)

    @staticmethod
    def _ssl_context():
        # certifi gives Android a bundled CA list; retain certificate
        # verification and fall back to Python's system trust store if absent.
        if certifi is not None:
            try:
                ca_file = certifi.where()
                if ca_file and os.path.isfile(ca_file):
                    return ssl.create_default_context(cafile=ca_file)
            except (OSError, AttributeError):
                pass
        return ssl.create_default_context()

    def _request(self, path, method="GET", payload=None, extra_headers=None, _retry=True):
        if not self.configured:
            raise BackendError("Backend is not configured. Add the Supabase URL and anon key to backend_config.json.")
        data = None if payload is None else json.dumps(payload).encode("utf-8")
        headers = {"apikey": self.anon_key, "Content-Type": "application/json"}
        if self.access_token:
            headers["Authorization"] = "Bearer " + self.access_token
        if extra_headers:
            headers.update(extra_headers)
        req = urllib.request.Request(self.url + path, data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=20, context=self._ssl_context()) as response:
                raw = response.read().decode("utf-8")
                if not raw:
                    return None
                try:
                    return json.loads(raw)
                except ValueError as exc:
                    raise BackendError("Supabase returned an unreadable response.") from exc
        except urllib.error.HTTPError as exc:
            # Access tokens last ~1 hour; renew once with the refresh token, then retry.
            if exc.code == 401 and _retry and self.refresh_token and not path.startswith("/auth/"):
                if self._refresh_session():
                    return self._request(path, method, payload, extra_headers, _retry=False)
                raise BackendError("Your session expired. Please sign out and sign in again.") from exc
            try:
                body = json.loads(exc.read().decode("utf-8"))
                message = body.get("msg") or body.get("message") or body.get("error_description") or body.get("error") or str(exc)
            except Exception:
                message = str(exc)
            raise BackendError(message) from exc
        except urllib.error.URLError as exc:
            reason = getattr(exc, "reason", exc)
            if isinstance(reason, ssl.SSLError):
                detail = "Secure connection failed (SSL certificate/TLS error). Runtime detail: " + str(reason)
            elif isinstance(reason, socket.gaierror):
                detail = "The server address could not be found (DNS error)."
            elif isinstance(reason, (TimeoutError, socket.timeout)):
                detail = "The server took too long to respond (timeout)."
            elif isinstance(reason, ConnectionRefusedError):
                detail = "The server refused the connection."
            elif isinstance(reason, OSError):
                detail = "Network connection failed: " + str(reason)
            else:
                detail = "Network request failed: " + str(reason)
            raise BackendError("Could not reach Pendo's backend. " + detail + " Check your internet connection and Supabase project status, then try again.") from exc
        except (TimeoutError, socket.timeout) as exc:
            raise BackendError("Could not reach Pendo's backend. The server took too long to respond (timeout).") from exc
        except ssl.SSLError as exc:
            raise BackendError("Could not reach Pendo's backend. Secure connection failed (SSL certificate/TLS error).") from exc
        except OSError as exc:
            raise BackendError("Could not reach Pendo's backend. Network connection failed: " + str(exc)) from exc

    def sign_in(self, email, password):
        result = self._request("/auth/v1/token?grant_type=password", "POST", {"email": email, "password": password})
        if not result:
            raise BackendError("Sign-in failed. Please try again.")
        self._set_session(result)
        return self.user

    def _refresh_session(self):
        token = self.refresh_token
        self.access_token = None  # don't send the expired token to the refresh endpoint
        try:
            result = self._request("/auth/v1/token?grant_type=refresh_token", "POST",
                                   {"refresh_token": token}, _retry=False)
        except BackendError:
            self.refresh_token = None
            return False
        if not result or not result.get("access_token"):
            self.refresh_token = None
            return False
        self.access_token = result.get("access_token")
        self.refresh_token = result.get("refresh_token") or token
        return True

    def _auth_redirect_url(self):
        """Return the optional app callback URL configured for Supabase Auth."""
        try:
            with open(self.config_path, "r", encoding="utf-8") as config_file:
                config = json.load(config_file)
            if not isinstance(config, dict):
                return ""
            configured = str(config.get("auth_redirect_url", "") or "").strip()
            return configured or self.AUTH_CALLBACK_URL
        except (OSError, ValueError, TypeError):
            return ""

    @staticmethod
    def _with_redirect(path, redirect_url):
        if not redirect_url:
            return path
        separator = "&" if "?" in path else "?"
        return path + separator + urllib.parse.urlencode({"redirect_to": redirect_url})

    def sign_up(self, email, password):
        # Supabase otherwise falls back to the project's Site URL, which is
        # commonly left at localhost during development. Configure
        # auth_redirect_url with an allowed production/app callback URL.
        path = self._with_redirect("/auth/v1/signup", self._auth_redirect_url())
        result = self._request(path, "POST", {"email": email, "password": password}) or {}
        if result.get("access_token"):
            self._set_session(result)
        return result

    def reset_password(self, email):
        path = self._with_redirect("/auth/v1/recover", self._auth_redirect_url())
        return self._request(path, "POST", {"email": email})

    def complete_auth_callback(self, callback_url):
        """Validate and complete a Supabase implicit-flow Android deep link."""
        try:
            parsed = urllib.parse.urlsplit(str(callback_url or ""))
        except ValueError as exc:
            raise BackendError("The sign-in link is invalid.") from exc
        expected = urllib.parse.urlsplit(self.AUTH_CALLBACK_URL)
        if parsed.scheme != expected.scheme or parsed.netloc != expected.netloc:
            raise BackendError("This sign-in link is not for Pendo.")

        params = urllib.parse.parse_qs(parsed.fragment)
        for key, values in urllib.parse.parse_qs(parsed.query).items():
            params.setdefault(key, values)

        error = (params.get("error_description") or params.get("error") or [""])[0]
        if error:
            raise BackendError(urllib.parse.unquote(error.replace("+", " ")))

        access_token = (params.get("access_token") or [""])[0]
        refresh_token = (params.get("refresh_token") or [""])[0]
        token_hash = (params.get("token_hash") or [""])[0]
        auth_type = (params.get("type") or ["signup"])[0]

        if token_hash:
            result = self._request(
                "/auth/v1/verify", "POST",
                {"token_hash": token_hash, "type": auth_type}
            ) or {}
            self._set_session(result)
        elif access_token and refresh_token:
            self.access_token = access_token
            self.refresh_token = refresh_token
            self.user = self._request("/auth/v1/user", "GET")
        else:
            raise BackendError("The link did not contain a valid Pendo sign-in session. Request a new email and try again.")

        if not self.access_token or not self.user:
            raise BackendError("Supabase did not return a valid account session. Please sign in again.")
        return {"type": auth_type, "user": self.user}

    def update_password(self, new_password):
        if not self.access_token:
            raise BackendError("Your password-reset session has expired. Request a new reset email.")
        if not isinstance(new_password, str) or len(new_password) < 8:
            raise BackendError("Use a password with at least 8 characters.")
        result = self._request("/auth/v1/user", "PUT", {"password": new_password})
        if isinstance(result, dict) and result:
            self.user = result
        return self.user

    def _set_session(self, result):
        self.access_token = result.get("access_token")
        self.refresh_token = result.get("refresh_token")
        self.user = result.get("user") or {}

    def get_profile(self):
        user_id = (self.user or {}).get("id")
        if not user_id:
            raise BackendError("Please sign in again.")
        rows = self._request(f"/rest/v1/profiles?id=eq.{user_id}&select=id,display_name,plan")
        return rows[0] if rows else None

    def upsert_profile(self, display_name=None, plan=None):
        user_id = (self.user or {}).get("id")
        if not user_id:
            raise BackendError("Please sign in again.")
        payload = {"id": user_id}
        if display_name is not None:
            payload["display_name"] = display_name
        if plan is not None:
            payload["plan"] = plan
        rows = self._request("/rest/v1/profiles", "POST", payload,
                            {"Prefer": "resolution=merge-duplicates,return=representation"})
        return rows[0] if rows else payload

    def save_record(self, record_type, content):
        if not self.user:
            raise BackendError("Please sign in to save data to the cloud.")
        rows = self._request("/rest/v1/app_records", "POST", {"record_type": record_type, "content": content},
                            {"Prefer": "return=representation"})
        return rows[0] if rows else None

    def list_records(self, record_type):
        if not self.user:
            raise BackendError("Please sign in to load cloud data.")
        safe_type = urllib.parse.quote(record_type, safe="")
        return self._request(f"/rest/v1/app_records?record_type=eq.{safe_type}&select=id,record_type,content,created_at&order=created_at.desc")

    def update_record(self, record_id, content):
        if not self.user:
            raise BackendError("Please sign in to update cloud data.")
        safe_id = urllib.parse.quote(str(record_id), safe="")
        user_id = urllib.parse.quote(str((self.user or {}).get("id", "")), safe="")
        rows = self._request(
            f"/rest/v1/app_records?id=eq.{safe_id}&user_id=eq.{user_id}",
            "PATCH", {"content": content},
            {"Prefer": "return=representation"}
        )
        if not rows:
            raise BackendError("That record could not be found or is no longer available.")
        return rows[0]

    def delete_record(self, record_id):
        if not self.user:
            raise BackendError("Please sign in to delete cloud data.")
        safe_id = urllib.parse.quote(str(record_id), safe="")
        user_id = urllib.parse.quote(str((self.user or {}).get("id", "")), safe="")
        self._request(
            f"/rest/v1/app_records?id=eq.{safe_id}&user_id=eq.{user_id}",
            "DELETE"
        )

    def sign_out(self):
        try:
            if self.access_token:
                self._request("/auth/v1/logout", "POST")
        finally:
            self.access_token = None
            self.refresh_token = None
            self.user = None
