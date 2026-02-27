import re
from typing import Optional
from src.models import NormalizedLog

REVERSE_SHELL_PATTERN = re.compile(r"(?i)(bash -i|nc .* -e|nc -l|/dev/tcp/|powershell -enc)")
PRIV_ESC_PATTERN = re.compile(r"(?i)(chmod 777|sudo su|setuid|setgid)")

def analyze(log: NormalizedLog) -> Optional[str]:
    ip = log.host.get("ip", "Unknown IP")
    original = log.event.get("original", "") or log.message or getattr(log, 'raw_message', '') or ""

    if REVERSE_SHELL_PATTERN.search(original):
        return f"💻 [EDR] Reverse and Bind Shell Experiment!\nSource: {ip}\nCommand: {original}"

    if PRIV_ESC_PATTERN.search(original):
        return f"💻 [EDR] Suspected Privilege Escalation!\nSource: {ip}\nCommand: {original}"

    return None