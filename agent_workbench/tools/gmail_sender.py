"""Gmail sender tool for manually confirmed Streamlit email sends."""

from __future__ import annotations

import base64
from dataclasses import dataclass
from email.mime.text import MIMEText
import os
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlparse


SCOPES = ["https://www.googleapis.com/auth/gmail.send"]
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CREDENTIALS_PATH = PROJECT_ROOT / "credentials.json"
PROXY_ENV_VARS = ("HTTPS_PROXY", "https_proxy", "HTTP_PROXY", "http_proxy")


@dataclass(frozen=True)
class GmailProxyConfig:
    """Parsed proxy configuration from the environment."""

    source: str
    url: str
    scheme: str
    host: str
    port: int
    username: str | None = None
    password: str | None = None


def is_gmail_configured(credentials_path: str = "credentials.json") -> bool:
    """Return whether a Gmail OAuth credentials file exists."""

    path = Path(credentials_path)
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    return path.exists()


def _resolve_project_path(path_value: str) -> Path:
    path = Path(path_value)
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    return path


def _normalize_proxy_url(proxy_url: str) -> str:
    cleaned = proxy_url.strip().strip("\"'").rstrip("\u3002").strip()
    if not cleaned:
        return ""
    if "://" not in cleaned:
        cleaned = f"http://{cleaned}"
    return cleaned


def _parse_proxy_url(proxy_url: str, source: str) -> GmailProxyConfig:
    normalized_url = _normalize_proxy_url(proxy_url)
    if not normalized_url:
        raise RuntimeError(f"Gmail proxy environment variable {source} is empty.")

    parsed = urlparse(normalized_url)
    scheme = parsed.scheme.lower()
    if scheme not in {"http", "socks4", "socks5"}:
        raise RuntimeError(
            f"Gmail proxy URL from {source} uses unsupported scheme '{parsed.scheme}'. "
            "Use http://host:port, socks4://host:port, or socks5://host:port."
        )

    host = parsed.hostname
    if not host:
        raise RuntimeError(
            f"Gmail proxy URL from {source} is missing a host: {proxy_url!r}."
        )

    try:
        port = parsed.port
    except ValueError as exc:
        raise RuntimeError(
            f"Gmail proxy URL from {source} has an invalid port: {proxy_url!r}."
        ) from exc

    if port is None:
        raise RuntimeError(
            f"Gmail proxy URL from {source} is missing a port: {proxy_url!r}."
        )

    username = unquote(parsed.username) if parsed.username else None
    password = unquote(parsed.password) if parsed.password else None
    return GmailProxyConfig(source, normalized_url, scheme, host, port, username, password)


def get_proxy_config_from_env() -> GmailProxyConfig | None:
    """Return the first supported Gmail proxy configured in the environment."""

    for env_name in PROXY_ENV_VARS:
        proxy_url = os.environ.get(env_name)
        if proxy_url and proxy_url.strip():
            return _parse_proxy_url(proxy_url, env_name)
    return None


def _load_credentials(token_path: str):
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
    except ImportError as exc:
        raise RuntimeError(
            "Gmail dependencies are missing. Install google-auth-oauthlib and google-api-python-client."
        ) from exc

    credentials_path = DEFAULT_CREDENTIALS_PATH
    resolved_token_path = _resolve_project_path(token_path)
    creds = None

    if resolved_token_path.exists():
        creds = Credentials.from_authorized_user_file(str(resolved_token_path), SCOPES)

    if creds and creds.valid:
        return creds

    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        if not credentials_path.exists():
            raise FileNotFoundError(
                f"Gmail credentials file not found: {credentials_path}. "
                "Create credentials.json first or keep using draft-only mode."
            )
        flow = InstalledAppFlow.from_client_secrets_file(str(credentials_path), SCOPES)
        creds = flow.run_local_server(port=0)

    resolved_token_path.write_text(creds.to_json(), encoding="utf-8")
    return creds


def _proxy_info_from_config(proxy_config: GmailProxyConfig):
    try:
        import httplib2
    except ImportError as exc:
        raise RuntimeError(
            "Gmail proxy support requires httplib2 and PySocks. "
            "Install dependencies from requirements.txt."
        ) from exc

    proxy_types = {
        "http": httplib2.socks.PROXY_TYPE_HTTP,
        "socks4": httplib2.socks.PROXY_TYPE_SOCKS4,
        "socks5": httplib2.socks.PROXY_TYPE_SOCKS5,
    }
    return httplib2.ProxyInfo(
        proxy_type=proxy_types[proxy_config.scheme],
        proxy_host=proxy_config.host,
        proxy_port=proxy_config.port,
        proxy_user=proxy_config.username,
        proxy_pass=proxy_config.password,
    )


def _build_gmail_service(build, creds):
    proxy_config = get_proxy_config_from_env()
    if proxy_config is None:
        return build("gmail", "v1", credentials=creds)

    try:
        import httplib2
        import google_auth_httplib2
    except ImportError as exc:
        raise RuntimeError(
            "Gmail proxy support requires google-auth-httplib2, httplib2, and PySocks. "
            "Install dependencies from requirements.txt."
        ) from exc

    proxy_info = _proxy_info_from_config(proxy_config)
    http = httplib2.Http(proxy_info=proxy_info)
    authorized_http = google_auth_httplib2.AuthorizedHttp(creds, http=http)
    return build("gmail", "v1", http=authorized_http)


def send_email(to: str, subject: str, body: str, token_path: str = "token.json") -> dict[str, Any]:
    """Send a plain-text email through the authorized Gmail account."""

    recipient = (to or "").strip()
    if not recipient:
        raise ValueError("Recipient email is required.")

    try:
        from googleapiclient.discovery import build
        from googleapiclient.errors import HttpError
    except ImportError as exc:
        raise RuntimeError(
            "Gmail dependencies are missing. Install google-auth-oauthlib and google-api-python-client."
        ) from exc

    creds = _load_credentials(token_path=token_path)
    message = MIMEText(body or "", "plain", "utf-8")
    message["to"] = recipient
    message["subject"] = subject or "Re: Your Inquiry"
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")

    try:
        service = _build_gmail_service(build, creds)
        result = service.users().messages().send(userId="me", body={"raw": raw}).execute()
    except HttpError as exc:
        status = getattr(getattr(exc, "resp", None), "status", "unknown")
        reason = getattr(getattr(exc, "resp", None), "reason", "")
        raise RuntimeError(
            f"Gmail API HTTP {status}: {reason or exc}. Original error: {exc}"
        ) from exc
    except RuntimeError:
        raise
    except Exception as exc:
        raise RuntimeError(f"Gmail API send failed: {type(exc).__name__}: {exc}") from exc

    return dict(result)
