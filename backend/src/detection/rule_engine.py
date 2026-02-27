from typing import Optional
from src.models import NormalizedLog
from src.notification.telegram import send_telegram_alert
from src.detection.brute_force import brute_force_detector
from src.detection import web_attacks, endpoint_detection


class DetectionEngine:
    def check_rules(self, log: NormalizedLog) -> Optional[str]:
        ip = log.host.get("ip", "Unknown IP")

        # Safe field extraction
        action = (log.event.get("action") or "").lower()
        original = (log.event.get("original") or "").lower()
        message = (log.message or "").lower()
        severity = (log.severity or "").upper()

        full_text = f"{action} {original} {message}"

        #  WAF RULE
        if "waf" in full_text:
            alert = (
                f"🛡️ [WAF Alert]\n"
                f"Source IP: {ip}\n"
                f"Event: {action}\n"
                f"Detail: {message}"
            )
            send_telegram_alert(alert)
            return alert

        # EDR RULE
        if "endpoint" in action or "process" in action:
            alert = endpoint_detection.analyze(log)
            if alert:
                send_telegram_alert(alert)
                return alert

        # BRUTE FORCE RULE
        if "login" in action and severity == "HIGH":
            alert = brute_force_detector.analyze(log)
            if alert:
                send_telegram_alert(alert)
                return alert

        # WEB ATTACKS (Manual HTTP logs vs.)
        if "web" in action or "http" in action:
            alert = web_attacks.analyze(log)
            if alert:
                send_telegram_alert(alert)
                return alert

        # CATCH-ALL HIGH
        if severity == "HIGH":
            alert = (
                f"⚠️ [CRITICAL SYSTEM ALERT]\n"
                f"Source IP: {ip}\n"
                f"Event: {action}\n"
                f"Detail: {message}"
            )
            send_telegram_alert(alert)
            return alert

        return None


# Global instance
rule_engine = DetectionEngine()