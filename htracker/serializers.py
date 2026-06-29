from rest_framework import serializers
from htracker.models import Habit
# ВАЖНО: Мы больше НЕ импортируем FieldFillingValidator и RelatedHabitValidator.
# Оставляем только простой валидатор для одного поля, если он нужен.
from htracker.validators import execution_time_validator


class HabitSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Habit
    """
    time_to_complete = serializers.DurationField(
        validators=[execution_time_validator],
        required=False
    )

    class Meta:
        model = Habit
        exclude = ("send_indicator",)
        # УДАЛИЛИ: validators = [...]
        # Здесь не должно быть сложных валидаторов, зависящих от нескольких полей.

    def validate(self, data):
        """
        бизнес-логика валидации.
        """
        instance = self.instance  # Старый объект из БД (если это обновление)

        # 1. Получаем актуальные значения.
        # Если поле есть в запросе (data) -> берем оттуда.
        # Если нет (значит, мы его не меняем) -> берем из старого объекта (instance).
        h_reward = data.get('h_reward', getattr(instance, 'h_reward', None))
        h_related = data.get('h_related', getattr(instance, 'h_related', None))
        h_pleasant = data.get('h_pleasant', getattr(instance, 'h_pleasant', False))

        # Вспомогательные проверки на заполненность
        is_reward_filled = h_reward is not None and str(h_reward).strip() != ""
        is_related_filled = h_related is not None

        # Конфликт Reward и Related
        if is_reward_filled and is_related_filled:
            raise serializers.ValidationError({
                'non_field_errors': [
                    "Нельзя одновременно указать и вознаграждение (h_reward), и связанную привычку (h_related)."
                ]
            })

        # Приятная привычка
        if h_pleasant:
            if is_reward_filled or is_related_filled:
                raise serializers.ValidationError({
                    'non_field_errors': [
                        "Приятная привычка не может иметь вознаграждения или связи с другой привычкой."
                    ]
                })
        else:
            # Полезная привычка (обязательные поля)
            if not is_reward_filled and not is_related_filled:
                raise serializers.ValidationError({
                    'non_field_errors': [
                        "Для полезной привычки обязательно нужно указать либо вознаграждение (h_reward), либо связать её с приятной привычкой (h_related)."
                    ]
                })

        # Проверка связанной привычки
        if is_related_filled and h_related:
            from htracker.models import Habit as HabitModel

            related_habit_obj = h_related

            # Если в запросе пришел ID (число), а не объект, нужно получить объект из БД
            if isinstance(related_habit_obj, int):
                try:
                    related_habit_obj = HabitModel.objects.get(pk=related_habit_obj)
                except HabitModel.DoesNotExist:
                    raise serializers.ValidationError({'h_related': ['Связанная привычка не найдена.']})

            # Проверка флага h_pleasant у связанной привычки
            if not related_habit_obj.h_pleasant:
                raise serializers.ValidationError({
                    'h_related': [
                        "Связанная привычка должна быть помечена как 'приятная' (h_pleasant=True)."
                    ]
                })

        return data

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data.pop('owner', None)

        if user.is_anonymous:
            raise serializers.ValidationError("Для создания привычки необходимо авторизоваться")

        habit = Habit.objects.create(
            owner=user,
            **validated_data
        )
        return habit