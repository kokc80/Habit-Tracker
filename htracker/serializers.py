from rest_framework import serializers
from htracker.models import Habit
from htracker.validators import (FieldFillingValidator, RelatedHabitValidator,
                               execution_time_validator)


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
        validators = [
            FieldFillingValidator(
                "h_reward",
                "h_related",
                "h_pleasant"
            ),
            RelatedHabitValidator("h_related"),
        ]
