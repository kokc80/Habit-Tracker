from rest_framework import serializers
from htracker.serializers import h_trackerSerializer
from users.models import User


class UserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели User
    """
    h_tracker = h_trackerSerializer(source="users_h_tracker", many=True, read_only=True)

    class Meta:
        model = User
        fields = "__all__"