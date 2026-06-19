import requests
from htracker.models import Habit
from htracker.services import send_tg_msg


@shared_task
def send_message(pk) -> None:
    """Sends reminders to user's telegram."""
    habit = Habit.objects.get(pk=pk)
    text = (
        f"Время для выполнения {habit.h_action} at {habit.h_place}! "
        f"Не забудьте {habit.h_reward if habit.h_reward else habit.h_related} после выполнения"
    )
    params = {
        "text": text,
        "chat_id": habit.user.tg_chat_id,
    }
    requests.get(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage", params=params)
