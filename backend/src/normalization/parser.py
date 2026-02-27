import uuid
from datetime import datetime
from src.models import RawLog, NormalizedLog

class LogParser:

    @staticmethod
    def normalize(raw: RawLog) -> NormalizedLog:
        """
        Takes the raw log, validates the security level, and converts it into a standardized format.
        Respects the agent's custom payload but uses fallback rules if data is missing.
        """
        
        # Severity Management
        valid_levels = {"LOW", "MEDIUM", "HIGH", "CRITICAL"}

        # If the agent specifies a severity, validate and use it
        if raw.severity:
            sev = raw.severity.upper()
            severity = sev if sev in valid_levels else "LOW"
        else:
            # Fallback rule engine for agents that don't specify severity
            type_lower = raw.event_type.lower()
            if any(x in type_lower for x in ['fail', 'error', 'attack', 'breach']):
                severity = "HIGH"
            elif 'warning' in type_lower:
                severity = "MEDIUM"
            else:
                severity = "LOW"

        #  Timestamp Management
        log_timestamp = datetime.utcnow()
        if raw.timestamp:
            try:
                log_timestamp = datetime.fromisoformat(raw.timestamp)
            except ValueError:
                pass 

        # Normalization & Model Transformation
        return NormalizedLog(
            id=str(uuid.uuid4()),
            timestamp=log_timestamp,
            severity=severity,
            host={
                "ip": raw.source_ip,
                "name": raw.device_id
            },
            event={
                "action": raw.action,          
                "category": raw.event_type,    
                "original": raw.raw_message
            },
            
            message=raw.message or f"[{severity}] Event '{raw.event_type}' detected from {raw.device_id}"
        )