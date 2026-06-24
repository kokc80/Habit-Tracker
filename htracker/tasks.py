from celery import shared_task
import logging

from htracker.models import Habit
from htracker.services import send_tg_msg

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_message(self, pk: int) -> None:
    try:
        habit = Habit.objects.get(pk=pk)
    except Habit.DoesNotExist:
        logger.warning("Habit with pk=%s not found. Skipping.", pk)
        return

    owner = habit.owner
    if not owner or not owner.tg_chat_id:
        logger.warning("No Telegram chat_id for habit pk=%s. Skipping.", pk)
        return

    text = (
        f"Время для выполнения {habit.h_action} at {habit.h_place}! "
        f"Не забудьте {habit.h_reward if habit.h_reward else habit.h_related} после выполнения"
    )

    success = send_tg_msg(owner.tg_chat_id, text)
    if not success:
        # Если send_tg_msg вернул False, решаем, нужно ли повторять
        # Например, можно поднять ошибку, чтобы сработал retry
        raise self.retry(exc=RuntimeError("Telegram send failed"))