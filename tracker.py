import os
import requests
from datetime import datetime

TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

def send_message(text):
    requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        data={
            "chat_id": CHAT_ID,
            "text": text
        },
        timeout=30
    )

send_message(
    f"✅ Cabela's Tracker успешно запущен!\n"
    f"Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
)

print("Test message sent")
