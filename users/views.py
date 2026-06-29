from django.contrib.auth.models import User
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny

from users.serializers import UserSerializer



class UserCreateAPIView(CreateAPIView):
    """
    Контролер создания пользователя
    """

    permission_classes = [AllowAny]
    serializer_class = UserSerializer

    def perform_create(self, serializer):
        # Получаем данные из сериализатора без сохранения
        user = serializer.save(is_active=True)
        # Устанавливаем пароль через сериализатор или напрямую
        password = serializer.validated_data.get("password")
        if password:
            user.set_password(password)
            user.save()
        else:
            # Если пароля нет, сохраняем без изменения пароля
            user.save()
