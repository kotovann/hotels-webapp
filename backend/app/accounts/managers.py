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
            password=password,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
        self,  email, phone_number, last_name, first_name, password,
        **extra_fields
    ):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Суперпользователь должен иметь is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Суперпользователь должен иметь is_superuser=True.')

        return self.create_user(
            email=email,
            phone_number=phone_number,
            last_name=last_name,
            first_name=first_name,
            password=password,
            **extra_fields
        )
