from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model
    """
    project_name = serializers.CharField(source='project.project_name', read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'fio_name', 'email', 'project', 'project_name',
            'first_login', 'is_active', 'date_joined', 'last_login'
        ]
        read_only_fields = ['id', 'date_joined', 'last_login']


class UserCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating User with temporary password
    """
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ['username', 'fio_name', 'email', 'project', 'password']

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = User.objects.create(**validated_data)
        if password:
            user.set_password(password)
        else:
            from django.utils.crypto import get_random_string
            temp_password = get_random_string(12)
            user.set_password(temp_password)
            user._temp_password = temp_password  # For response
        user.first_login = True
        user.save()
        return user


class PasswordChangeSerializer(serializers.Serializer):
    """
    Serializer for changing password on first login
    """
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, min_length=8)
    confirm_password = serializers.CharField(required=True)

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError("New passwords do not match")
        return data