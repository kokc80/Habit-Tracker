import logging
import requests
from requests.exceptions import RequestException, Timeout, ConnectionError

from config import settings

logger = logging.getLogger(__name__)

TG_BASE_URL = f"https://api.telegram.org/bot{settings.TG_TOKEN}"

def send_tg_msg(chat_id: int, msg: str, parse_mode: str | None = None) -> bool:
    """
    Отправляет сообщение в Telegram.
    Возвращает True при успехе, False при неудаче (чтобы вызывающий код мог решить, что делать).
    """
    payload = {
        "chat_id": chat_id,
        "text": msg,
    }
    if parse_mode:
        payload["parse_mode"] = parse_mode

    try:
        resp = requests.post(
            f"{TG_BASE_URL}/sendMessage",
            json=payload,
            timeout=10,  # 10 секунд — достаточно для Telegram
        )
        resp.raise_for_status()
        return True
    except Timeout:
        logger.warning("Telegram send timed out for chat_id=%s", chat_id)
        return False
    except ConnectionError:
        logger.warning("Connection error while sending to Telegram chat_id=%s", chat_id)
        return False
    except RequestException as e:
        # Сюда попадут и HTTP-ошибки (4xx, 5xx) после raise_for_status
        status = getattr(e.response, "status_code", None) if e.response else None
        logger.error(
            "Telegram send failed for chat_id=%s, status=%s, error=%s",
            chat_id,
            status,
            e,
        )
        # Частые «неисправимые» ошибки: 403 (бот заблокирован), 400 (неверный запрос)
        if status in (403, 400):
            logger.info("Not retrying due to non-retryable status code %s", status)
        return False
