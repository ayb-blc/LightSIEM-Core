from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

# --- 1. INPUT MODEL (Raw Log) ---
# The raw data format received from endpoints (ESP8266, Linux agents, etc.)
class RawLog(BaseModel):
    source_ip: str = Field(..., description="IP address of the device sending the log")
    device_id: str = Field(..., description="Unique identifier of the device (MAC or Hostname)")
    event_type: str = Field(..., description="Type of the event (e.g., login_failed, physical_security)")
    
    # Optional fields that smart agents (like IoT sensors) might send
    action: Optional[str] = None
    severity: Optional[str] = None
    message: Optional[str] = None
    
    raw_message: Optional[str] = None
    timestamp: Optional[str] = None # Will be auto-assigned if not provided by the agent

# --- 2. OUTPUT MODEL (Normalized Log) ---
# The standardized language understood by the SIEM (Similar to Elastic Common Schema - ECS)
class NormalizedLog(BaseModel):
    id: str
    timestamp: datetime
    severity: str  # LOW, MEDIUM, HIGH, CRITICAL
    host: Dict[str, str]  # e.g., {"ip": "192.168.1.116", "name": "esp8266-server-room-01"}
    event: Dict[str, Any] # e.g., {"action": "gas_leak_detected", "category": "physical_security"}
    message: str