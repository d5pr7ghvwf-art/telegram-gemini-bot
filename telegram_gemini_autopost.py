import os
from datetime import datetime
import requests
from google import genai

TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
TG_CHANNEL_ID = os.environ["TG_CHANNEL_ID"]

BASE_PROMPT = "Какой сегодня день месяца? Сегодня {} число."
MODEL = "gemini-1.5-flash"

def get_gemini_response(day_number: int) -> str:
    client = genai.Client(api_key=GEMINI_API_KEY)
    prompt = BASE_PROMPT.format(day_number)
    response = client.models.generate_content(model=MODEL, contents=prompt)
    return response.text or ""

def send_to_telegram(text: str) -> None:
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    requests.post(url, data={
        "chat_id": TG_CHANNEL_ID,
        "text": text
    }, timeout=30).raise_for_status()

day_number = datetime.now().day
answer = get_gemini_response(day_number)
post_text = f"🗓 Ежедневный отчет — {day_number} число\n\n{answer}"
send_to_telegram(post_text)
