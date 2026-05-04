from django.db import transaction
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ValidationError
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from rest_framework import serializers

from utils.validators import validate_email
from utils.normalizers import normalize_email


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)
    short_name = serializers.CharField(read_only=True)
    role = serializers.CharField(read_only=True)
    password = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = (
            'email', 'phone_number', 'first_name', 'middle_name', 'last_name', 'full_name',
            'short_name', 'date_of_birth', 'last_login', 'date_joined', 'password', 'role'
        )
        read_only_fields = ('full_name', 'short_name', 'last_login', 'date_joined', 'role')


class GuestSerializer(UserSerializer):
    @transaction.atomic
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        user.assign_role(User.Role.GUEST)
        return user


class ModeratorSerializer(UserSerializer):
    @transaction.atomic
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        user.assign_role(User.Role.MODERATOR)
        return user


class AdministratorSerializer(UserSerializer):
    @transaction.atomic
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        user.assign_role(User.Role.ADMIN)
        return user


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate_email(self, value):
        if not validate_email(value):
            raise serializers.ValidationError('Не является валидным email')
        return normalize_email(value)


class ResetPasswordConfirmSerializer(serializers.Serializer):
    uid = serializers.CharField(required=True)
    token = serializers.CharField(required=True)
    new_password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    new_password_confirm = serializers.CharField(write_only=True, required=True)

    def validate(self, data):
        if data['new_password'] != data['new_password_confirm']:
            raise serializers.ValidationError(
                {'new_password_confirm': 'Пароли не совпадают'}
            )

        try:
            uid = force_str(urlsafe_base64_decode(data['uid']))
            user = User.objects.get(pk=uid)
        except (User.DoesNotExist, ValueError, TypeError) as e:
            raise serializers.ValidationError({'uid': 'Недействительная ссылка'}) from e

        if not default_token_generator.check_token(user, data['token']):
            raise serializers.ValidationError({'token': 'Токен недействителен или истёк'})

        data['user'] = user
        return data


class AssignRoleSerializer(serializers.Serializer):
    role = serializers.ChoiceField(choices=User.Role.choices, required=True)

    def validate(self, data):
        role = data['role']
        if role not in User.Role.values:
            raise ValidationError(f'Невозможно присвоить пользователю роль "{role}"')
        return data


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = (
            'email', 'first_name', 'last_name',
            'phone_number', 'password', 'password_confirm'
        )

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise ValidationError('Пользователь с таким email уже существует')
        return value

    def validate_phone_number(self, value):
        if User.objects.filter(phone_number=value).exists():
            raise ValidationError('Номер телефона уже используется')
        return value

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise ValidationError({'password_confirm': 'Пароли не совпадают'})
        return data

    @transaction.atomic
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        user.assign_role(User.Role.GUEST)
        return user
