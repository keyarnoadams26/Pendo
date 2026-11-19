"""Small Supabase REST/Auth client for Pendo; uses Python stdlib only."""
from __future__ import annotations
import json
import os
import urllib.error
import urllib.request
import urllib.parse


class BackendError(Exception):
    pass


class PendoBackend:
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
            self.url = str(cfg.get("supabase_url", "")).strip().rstrip("/")
            self.anon_key = str(cfg.get("supabase_anon_key", "")).strip()
        except (OSError, ValueError):
            self.url, self.anon_key = "", ""

    @property
    def configured(self):
        return bool(self.url.startswith("https://") and self.anon_key)

    def _request(self, path, method="GET", payload=None, extra_headers=None):
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
            with urllib.request.urlopen(req, timeout=15) as response:
                raw = response.read().decode("utf-8")
                return json.loads(raw) if raw else None
        except urllib.error.HTTPError as exc:
            try:
                body = json.loads(exc.read().decode("utf-8"))
                message = body.get("msg") or body.get("message") or body.get("error_description") or body.get("error") or str(exc)
            except Exception:
                message = str(exc)
            raise BackendError(message) from exc
        except (urllib.error.URLError, TimeoutError) as exc:
            raise BackendError("Could not reach Pendo's backend. Check your connection and try again.") from exc

    def sign_in(self, email, password):
        result = self._request("/auth/v1/token?grant_type=password", "POST", {"email": email, "password": password})
        self._set_session(result)
        return self.user

    def sign_up(self, email, password):
        result = self._request("/auth/v1/signup", "POST", {"email": email, "password": password})
        if result.get("access_token"):
            self._set_session(result)
        return result

    def reset_password(self, email):
        redirect_url = ""
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                redirect_url = str(json.load(f).get("auth_redirect_url", "")).strip()
        except (OSError, ValueError, TypeError):
            pass
        path = "/auth/v1/recover"
        if redirect_url:
            path += "?redirect_to=" + urllib.parse.quote(redirect_url, safe="")
        return self._request(path, "POST", {"email": email})

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

    def sign_out(self):
        try:
            if self.access_token:
                self._request("/auth/v1/logout", "POST")
        finally:
            self.access_token = None
            self.refresh_token = None
            self.user = None
