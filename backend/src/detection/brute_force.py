from datetime import datetime, timedelta
from typing import Dict, List, Optional
from src.models import NormalizedLog

class BruteForceDetector:
    def __init__(self):
        self.failed_login_attempts: Dict[str, List[datetime]] = {}
        self.WINDOW_SECONDS = 60
        self.THRESHOLD = 5

    def analyze(self, log: NormalizedLog) -> Optional[str]:
        ip = log.host.get("ip")
        if not ip:
            return None
        
        now = datetime.utcnow()
        if ip not in self.failed_login_attempts:
            self.failed_login_attempts[ip] = []

        self.failed_login_attempts[ip].append(now)
        
        cutoff_time = now - timedelta(seconds=self.WINDOW_SECONDS)
        self.failed_login_attempts[ip] = [
            t for t in self.failed_login_attempts[ip] if t > cutoff_time
        ]

        if len(self.failed_login_attempts[ip]) >= self.THRESHOLD:
            self.failed_login_attempts[ip] = [] 
            return f"BRUTE FORCE DETECTED: {ip} -> {self.THRESHOLD} failed attempts in {self.WINDOW_SECONDS}s"

        return None

brute_force_detector = BruteForceDetector()