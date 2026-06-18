from datetime import timedelta
from rest_framework.validators import ValidationError


class FieldFillingValidator:
    """
    Проверка заполнения полей reward и h_related
    """
    def __init__(self, h_reward, h_related, h_pleasant):
        self.h_reward = h_reward
        self.h_related = h_related
        self.h_pleasant = h_pleasant

    def __call__(self, value):
        h_reward_field = value.get(self.h_reward)
        h_related_field = value.get(self.h_related)
        h_pleasant_field = value.get(self.h_pleasant)

        if h_reward_field and h_related_field:
            raise ValidationError(
                "Может быть заполнено поле reward или поле h_related"
            )
        if h_pleasant_field:
            if h_reward_field or h_related_field:
                raise ValidationError(
                    "У приятной привычки не может быть связанной привычки или вознаграждения"
                )
        else:
            if not h_reward_field and not h_related_field:
                raise ValidationError(
                    "Поле reward или поле related_habit обязательно для заполнения у полезной привычки"
                )


class RelatedHabitValidator:
    """
    Валидатор для проверки связанной привычки на принадлежность к приятной привычки
    """
    def __init__(self, h_related):
        self.h_related = h_related

    def __call__(self, value):
        habit = value.get(self.h_related)
        if habit:
            if not habit.h_pleasant:
                raise ValidationError("Связанная привычка должна быть приятной")


def execution_time_validator(value):
    """
    Валидатор для проверки продолжительности выполнения привычки не более 120 секунд
    """
    if value:
        if value > timedelta(seconds=120):
            raise ValidationError(
                "Продолжительность выполнения привычки не может быть более 120 секунд"
            )
