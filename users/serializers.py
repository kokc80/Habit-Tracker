from django.contrib.auth.models import User
from rest_framework.serializers import ModelSerializer

from users.models import User


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data.get("email", ""), password=validated_data["password"]
        )
        return user

