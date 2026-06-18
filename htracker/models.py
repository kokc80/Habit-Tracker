from datetime import timedelta

from django.core.validators import MaxValueValidator
from django.db import models

from users.models import User

NULLABLE = {"null": True, "blank": True}


class Habit(models.Model):
    """ Модель привычки """
    habit = models.CharField(
        max_length=255,
        verbose_name="Привычка",
    )
    h_place = models.CharField(
        max_length=255, verbose_name="Место где нужно выполнять привычку",
        **NULLABLE
    )
    h_time = models.TimeField(
        verbose_name="Время когда выполняется привычка",
        **NULLABLE
    )
    h_action = models.CharField(
        max_length=255, verbose_name="Действие, которое представляет собой привычка",
        **NULLABLE
    )
    h_pleasant = models.BooleanField(
        verbose_name="Показатель приятной привычки",
        default=False
    )
    h_related = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        verbose_name="Связанная приятная привычка",
        **NULLABLE,
        related_name="related_habits"
    )
    h_period = models.PositiveSmallIntegerField(
        validators=[MaxValueValidator(7)],
        verbose_name="Периодичность привычки в неделю",
        default=1
    )
    h_reward = models.CharField(
        verbose_name="Вознаграждение за привычку",
        **NULLABLE
    )
    h_duration = models.DurationField(
        default=timedelta(seconds=120),
        verbose_name="Продолжительность выполнения привычки по времени",
    )

    STATUS_PUBLISHED = [
        ("Опубликован", "Опубликован"),
        ("Не опубликован", "Не опубликован"),
    ]
    published = models.CharField(
        max_length=50,
        choices=STATUS_PUBLISHED,
        default="Не опубликован",
        verbose_name="Статус опубликования привычки",
    )
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Создатель привычки",
        related_name="users_habits",
        **NULLABLE
    )
    send_indicator = models.PositiveSmallIntegerField(
        editable=False,
        verbose_name="Индикатор отправки",
        **NULLABLE
    )

    class Meta:
        verbose_name = "Привычка"
        verbose_name_plural = "Привычки"
        ordering = ("id",)

    def __str__(self):
        return self.habit