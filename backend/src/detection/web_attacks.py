import re
from typing import Optional
from src.models import NormalizedLog

# Regex Rule
INJECTION_PATTERN = re.compile(r"(?i)(union.*select|select.*from|drop\s+table|;.*rm\s+-rf|\|.*whoami)")
XSS_PATTERN = re.compile(r"(?i)(<script>|javascript:|onerror=|onload=)")

def analyze(log: NormalizedLog) -> Optional[str]:
    ip = log.host.get("ip", "Unknown IP")
    message = log.message or getattr(log, 'raw_message', '') or ""
    
    if INJECTION_PATTERN.search(message):
        return f"[OWASP A03: Injection] SQL/Command Injection Attempt -> {ip}\nLog: {message}"
    elif XSS_PATTERN.search(message):
        return f"[OWASP A03: Injection] XSS Attempt -> {ip}\nLog: {message}"
    
    return None