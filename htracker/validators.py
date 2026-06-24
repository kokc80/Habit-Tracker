from datetime import timedelta
from rest_framework.validators import ValidationError


def execution_time_validator(value):
    """
    Валидатор для проверки продолжительности выполнения привычки не более 120 секунд
    """
    if value:
        if value > timedelta(seconds=120):
            raise ValidationError(
                "Продолжительность выполнения привычки не может быть более 120 секунд"
            )
