"""Gmail sender tool for manually confirmed Streamlit email sends."""

from __future__ import annotations

import base64
from email.mime.text import MIMEText
from pathlib import Path
from typing import Any


SCOPES = ["https://www.googleapis.com/auth/gmail.send"]
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CREDENTIALS_PATH = PROJECT_ROOT / "credentials.json"


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
        service = build("gmail", "v1", credentials=creds)
        result = service.users().messages().send(userId="me", body={"raw": raw}).execute()
    except HttpError as exc:
        status = getattr(getattr(exc, "resp", None), "status", "unknown")
        reason = getattr(getattr(exc, "resp", None), "reason", "")
        raise RuntimeError(f"Gmail API HTTP {status}: {reason or exc}") from exc

    return dict(result)

