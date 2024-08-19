from django.contrib.auth import get_user_model
from djoser.serializers import UserSerializer
from rest_framework import serializers

from users.models import Subscription

User = get_user_model()


class CustomUserSerializer(UserSerializer):
    """Сериализатор пользователей."""

    class Meta:
        model = User


class SubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор подписки."""

    course_title = serializers.CharField(source='course.title', read_only=True)
    group_name = serializers.CharField(source='group.name', read_only=True)
    user_full_name = serializers.CharField(source='user.get_full_name', read_only=True)

    class Meta:
        model = Subscription
        fields = (
            'id',
            'course',
            'course_title',
            'user',
            'user_full_name',
            'group',
            'group_name',
            'start_date',
            'end_date',
            'is_active',
        )
