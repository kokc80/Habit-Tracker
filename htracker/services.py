import requests
from config import settings


def send_tg_msg(chat_id, msg):
    params = {
        "text": msg,
        "chat_id": chat_id,
    }
    response = requests.get(f"{settings.TG_URL}{settings.TG_TOKEN}/sendMessage", params = params)