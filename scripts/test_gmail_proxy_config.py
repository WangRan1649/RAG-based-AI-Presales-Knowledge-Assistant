"""Local import and proxy parsing check for Gmail sender.

This script does not send email.
"""

from __future__ import annotations

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agent_workbench.tools.gmail_sender import get_proxy_config_from_env


proxy_config = get_proxy_config_from_env()
if proxy_config is None:
    print("detected proxy: <none>")
    print("proxy host: <none>")
    print("proxy port: <none>")
else:
    print(f"detected proxy: {proxy_config.url}")
    print(f"proxy host: {proxy_config.host}")
    print(f"proxy port: {proxy_config.port}")

print("gmail_sender import ok")