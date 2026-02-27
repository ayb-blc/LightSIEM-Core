import requests

# Enter your own token and ID information here
TELEGRAM_BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
TELEGRAM_CHAT_ID = "YOUR_BOT_CHAT_ID_HERE"

def send_telegram_alert(alert_message: str):
    """Sends SIEM alerts to the administrator via Telegram."""
    if not TELEGRAM_BOT_TOKEN or TELEGRAM_BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": f"🚨 CRITICAL SECURITY ALERT 🚨\n\n{alert_message}"
    }
    try:
        response = requests.post(url, json=payload, timeout=3)
        if response.status_code != 200:
            print(f"\033[91m[TELEGRAM API ERROR] Code: {response.status_code}, Detail: {response.text}\033[0m")
    except Exception as e:
        print(f"Telegram sending error: {e}")