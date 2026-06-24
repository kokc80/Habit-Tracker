from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from htracker.models import Habit
from users.models import User


class HabitTest(APITestCase):
    """Тестирование API для модели Habit"""

    def setUp(self):
        self.user = User.objects.create(email="test@test.ru")

        # Создаем объект строго по полям модели
        self.habit = Habit.objects.create(
            habit="test полезная привычка",
            h_place="test место",
            h_time="12:00",
            h_reward="test вознаграждение",
            owner=self.user,
            # Остальные поля возьмут значения по умолчанию
        )

        self.client.force_authenticate(user=self.user)

    def test_list_habit(self):
        """Тест получения списка привычек (без пагинации, судя по твоему логу)"""
        url = reverse("htracker:htracker-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        # ВАЖНО: Твой лог показал, что приходит просто список [ {...}, {...} ], а не {"results": [...]}
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)

        result = data[0]

        # Проверяем поля, используя имена из реального JSON (h_place, h_time и т.д.)
        self.assertEqual(result["habit"], "test полезная привычка")
        self.assertEqual(result["h_place"], "test место")
        self.assertEqual(result["h_time"], "12:00:00")  # Формат времени в ответе
        self.assertEqual(result["h_reward"], "test вознаграждение")
        self.assertEqual(result["owner"], self.user.pk)
        self.assertEqual(result["h_duration"], "00:02:00")

    def test_create_habit(self):
        """Тест создания привычки"""
        url = reverse("htracker:htracker-list")
        data = {
            "habit": "test1 новая привычка",
            "h_reward": "test1 награда",
            # Если сериализатор требует другие поля, добавь их сюда
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Habit.objects.count(), 2)

        created_habit = Habit.objects.last()
        self.assertEqual(created_habit.habit, "test1 новая привычка")
        self.assertEqual(created_habit.owner, self.user)

    def test_retrieve_habit(self):
        """Получение конкретной привычки"""
        url = reverse("htracker:htracker-detail", kwargs={"pk": self.habit.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["habit"], "test полезная привычка")

    def test_update_habit(self):
        """Тест на частичное обновление привычки"""
        url = reverse("htracker:htracker-detail", args=(self.habit.pk,))
        data = {"habit": "updated привычка"}

        response = self.client.patch(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["habit"], "updated привычка")

        updated_habit = Habit.objects.get(pk=self.habit.pk)
        self.assertEqual(updated_habit.habit, "updated привычка")

    def test_delete_habit(self):
        """Удаление привычки"""
        url = reverse("htracker:htracker-detail", args=(self.habit.pk,))
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        # Проверяем, что объект действительно удален из БД
        self.assertFalse(Habit.objects.filter(pk=self.habit.pk).exists())

    def test_user_habits_list(self):
        """Получение списка привычек текущего пользователя"""
        url = reverse("htracker:user_htracker_list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIsInstance(data, dict)

        # Проверяем наличие обязательных ключей пагинации
        self.assertIn("results", data)
        self.assertIn("count", data)

        results = data["results"]
        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 1)

        result = results[0]
        self.assertEqual(result["id"], self.habit.pk)
        self.assertEqual(result["habit"], self.habit.habit)
        self.assertEqual(result["owner"], self.user.pk)