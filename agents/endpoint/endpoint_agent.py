import time
import psutil
import requests

# SIEM Epicenter Settings
SIEM_URL = "http://localhost:8000/api/v1/ingest"
DEVICE_ID = "linux-endpoint-01"

# Malware/Suspicious Tools to Catch (Malware Signatures)
SUSPICIOUS_PROCESSES = ['nc', 'nmap', 'hydra', 'sqlmap', 'wireshark']

def send_to_siem(action, severity, message):
    payload = {
        "device_id": DEVICE_ID,
        "event_type": "endpoint_security",
        "action": action,
        "severity": severity,
        "message": message,
        "source_ip": "127.0.0.1" 
    }
    try:
        response = requests.post(SIEM_URL, json=payload, timeout=2)
        if response.status_code in [200, 202]:
            print(f"\033[92m[+] Forwarded to SIEM:\033[0m {message}")
    except Exception as e:
        print(f"\033[91m[!] The Epicenter could not be reached:\033[0m {e}")

def monitor_processes():
    print(f"🛡️ Endpoint Agent (EDR) Has Started! Suspicious transactions are monitored...")
    seen_pids = set()

    while True:
        # Scan all running processes in the system
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                pid = proc.info['pid']
                name = proc.info['name'].lower()
                
                # Check only newly opened transactions
                if pid not in seen_pids:
                    seen_pids.add(pid)
                    
                    # Is the transaction name on the blacklist?
                    
                    if name in SUSPICIOUS_PROCESSES:
                        cmd = " ".join(proc.info['cmdline']) if proc.info['cmdline'] else name
                        msg = f"[EDR ALARM] Suspicious Activity: {name} The vehicle was started! Full Command: {cmd}"
                            
                        # # Send Log to Center
                        send_to_siem("process_creation", "HIGH", msg)
                            
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        
        time.sleep(3)

if __name__ == "__main__":
    monitor_processes()