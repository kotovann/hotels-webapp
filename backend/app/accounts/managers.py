from django.db import transaction
from django.contrib.auth.models import BaseUserManager


class UserManager(BaseUserManager):
    def create_user(
        self, email, phone_number, last_name, first_name, password,
        **extra_fields
    ):
        if not email:
            raise ValueError('Email должен быть указан')
        if not phone_number:
            raise ValueError('Номер телефона должен быть указан')
        if not last_name:
            raise ValueError('Фамилия должна быть указана')
        if not first_name:
            raise ValueError('Имя должно быть указано')
        if not password:
            raise ValueError('Пароль должен быть указан')

        email = self.normalize_email(email)

        user = self.model(
            email=email,
            phone_number=phone_number,
            last_name=last_name,
            first_name=first_name,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    @transaction.atomic
    def create_superuser(
        self,  email, phone_number, last_name, first_name, password,
        **extra_fields
    ):
        extra_fields.setdefault('is_active', True)
        user = self.create_user(
            email=email,
            phone_number=phone_number,
            last_name=last_name,
            first_name=first_name,
            password=password,
            **extra_fields
        )

        from app.accounts.models import Administrator
        Administrator.objects.create(user=user)

        return user
