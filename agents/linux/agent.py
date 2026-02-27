import time
import socket
import re
import requests
import os

# --- Settings ---
BACKEND_URL = "http://localhost:8000/api/v1/ingest"
# auth.log for Ubuntu/Debian, secure for CentOS/RHEL
LOG_FILE = "/var/log/auth.log" 
DEVICE_ID = socket.gethostname()

# Regex to capture IP Address 
IP_PATTERN = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'

def follow(thefile):
    """
    Python version of the 'tail -f' command in Linux.
    It reads live the lines added to the end of the file.
    """
    thefile.seek(0, os.SEEK_END) 
    while True:
        line = thefile.readline()
        if not line:
            time.sleep(0.1) 
            continue
        yield line

def parse_and_send(line):
    """
    It analyzes the raw log line and sends it to the Backend.
    """
    line = line.strip()
    if not line:
        return

    # 1. Determine Event Type (Simple word hunt)
    event_type = "system_log"
    if "Accepted password" in line:
        event_type = "login_success"
    elif "Failed password" in line or "authentication failure" in line:
        event_type = "login_failed"
    elif "sudo" in line and "COMMAND" in line:
        event_type = "sudo_usage"
    
    # Only events we are interested in (To reduce noise)
    # Not all of them appear for now, but here 'if event_type ==...' can be added.

    # 2. Extract IP Address (with Regex)
    ip_match = re.search(IP_PATTERN, line)
    source_ip = ip_match.group(0) if ip_match else "127.0.0.1"

    # 3. JSON Package
    payload = {
        "source_ip": source_ip,
        "device_id": DEVICE_ID,
        "event_type": event_type,
        "raw_message": line
    }

    # 4. Send to Backend
    try:
        response = requests.post(BACKEND_URL, json=payload, timeout=2)
        print(f"[SENT] {event_type} -> {response.status_code}")
    except Exception as e:
        print(f"[ERROR] Backend unreachable: {e}")

if __name__ == "__main__":
    print(f"🕵️‍♂️  Linux Agent Started: {DEVICE_ID}")
    print(f"📂 Tracked File: {LOG_FILE}")
    print("------------------------------------------------")

    try:
        with open(LOG_FILE, "r") as f:
            loglines = follow(f)
            for line in loglines:
                parse_and_send(line)
    except PermissionError:
        print("\n❌ ERROR: No permission to read the log file! Please run with 'sudo'")
    except FileNotFoundError:
        print(f"\n❌ ERROR: {LOG_FILE} not found. Are you in the right distro?")
    except KeyboardInterrupt:
        print("\n👋 The agent was stopped.")