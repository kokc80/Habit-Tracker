import os

from celery import Celery
# установка переменной окружения для настроек проекта
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

#Создание экземпляра объекта Celery
app = Celery("config")

#Загрузка настроек из файла django
app.config_from_object("django.conf:settings", namespace="CELERY")

# Обнаружение и регистрация задач
app.autodiscover_tasks()

# @app.task(bind=True, ignore_ressult=True)
# def debug_task(self):
#     print(f"Request: {self.request!r}")