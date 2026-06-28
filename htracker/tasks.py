from datetime import timezone, timedelta
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
        # retry сработает согласно max_retries и default_retry_delay
        raise self.retry(exc=RuntimeError("Telegram send failed"))


@shared_task()
def schedule_reminders():
    """
    Находит привычки, которым нужно напомнить ЗА 15 МИНУТ до h_time.
    Использует last_reminder_date для защиты от дублей в течение суток.
    """
    now = timezone.now()
    today = now.date()
    current_time = now.time()

    window_minutes = 15

    habits = Habit.objects.filter(
        is_active=True,
        h_time__isnull=False,
    )

    for habit in habits:
        h_time = habit.h_time

        # Создаём datetime с фиктивной датой, чтобы корректно вычесть timedelta
        dummy_dt = timezone.make_aware(timezone.datetime(2000, 1, 1))
        h_dt = dummy_dt.replace(
            hour=h_time.hour,
            minute=h_time.minute,
            second=h_time.second,
            microsecond=h_time.microsecond,
        )
        start_window_dt = h_dt - timedelta(minutes=window_minutes)
        start_window_time = start_window_dt.time()

        in_window = False
        if start_window_time <= h_time:
            # Окно не пересекает полночь: [start, end)
            if start_window_time <= current_time < h_time:
                in_window = True
        else:
            # Окно пересекает полночь: [start, 23:59:59] ИЛИ [00:00:00, end)
            if current_time >= start_window_time or current_time < h_time:
                in_window = True

        if not in_window:
            continue

        # Защита от дублей: если сегодня уже напоминали — пропускаем
        if habit.last_reminder_date == today:
            continue

        # Отправляем напоминание через задачу
        send_message.delay(pk=habit.pk)

        # Помечаем, что сегодня уже напомнили
        habit.last_reminder_date = today
        habit.save(update_fields=["last_reminder_date"])