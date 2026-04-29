from django.db import models
from django.contrib.auth.models import AbstractUser, Group as BaseGroup

from phonenumber_field.modelfields import PhoneNumberField
from app.accounts.managers import UserManager


class Group(BaseGroup):
    '''
    Прокси-модель Group, добавляющая verbose_name.
    '''
    class Meta:
        proxy = True
        verbose_name = 'Группа пользователей'
        verbose_name_plural = 'Группы пользователей'
        ordering = ['name']


class User(AbstractUser):
    '''
    Кастомная модель пользователя, наследующая AbstractUser.
    В качестве идентификатора используется email, поле username отключено.
    '''
    class Role:
        GUEST = 'Гость'
        EMPLOYEE = 'Сотрудник'
        MODERATOR = 'Модератор'
        ADMIN = 'Администратор'
        OWNER = 'Владелец'

    username = None
    email = models.EmailField(
        max_length=100,
        unique=True,
        error_messages={'invalid': 'Введен некорректный email.'},
        verbose_name='Электронная почта',
        help_text='Обязательное поле, должно быть уникальным.'
    )
    phone_number = PhoneNumberField(
        null=False,
        blank=False,
        unique=True,
        error_messages={'invalid': 'Введите номер в формате +7XXXXXXXXXX или 8XXXXXXXXXX.'},
        verbose_name='Номер телефона',
    )
    first_name = models.CharField(
        max_length=100,
        verbose_name='Имя',
    )
    middle_name = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name='Отчество',
    )
    last_name = models.CharField(
        max_length=100,
        verbose_name='Фамилия',
    )
    date_of_birth = models.DateField(
        null=True,
        verbose_name='Дата рождения',
    )

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ('first_name', 'last_name', 'phone_number')
    objects = UserManager()

    class Meta:
        db_table = 'user'
        ordering = ['-date_joined']
        indexes = [
            models.Index(fields=['-date_joined']),
        ]
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    @property
    def full_name(self) -> str:
        '''
        Возвращает полное имя пользователя в формате:
        Имя Отчество Фамилия (если отчество указано) или Имя Фамилия.
        '''
        names = [self.last_name, self.first_name, self.middle_name]
        return ' '.join(filter(None, names))

    @property
    def short_name(self) -> str:
        '''
        Возвращает краткое имя: Фамилия И.О. или Фамилия И., если отчества нет.
        '''
        first_initial = f'{self.first_name[0]}.'
        middle_initial = f'{self.middle_name[0]}.' if self.middle_name else ''
        return f"{self.last_name} {first_initial}{middle_initial}"

    @property
    def is_admin(self) -> bool:
        return hasattr(self, 'admin')

    @property
    def is_moderator(self) -> bool:
        return hasattr(self, 'moderator')

    @property
    def is_employee(self) -> bool:
        return hasattr(self, 'employee')

    @property
    def is_owner(self) -> bool:
        return self.is_admin and self.admin.is_owner

    @property
    def is_superuser(self) -> bool:
        return self.is_owner

    @property
    def is_staff(self) -> bool:
        return self.is_employee or self.is_moderator or self.is_admin

    @is_superuser.setter
    def is_superuser(self, _):
        pass

    @is_staff.setter
    def is_staff(self, _):
        pass

    @property
    def role(self) -> str:
        '''
        Возвращает основную роль пользователя.
        '''
        if self.is_owner:
            return self.Role.OWNER
        if self.is_admin:
            return self.Role.ADMIN
        if self.is_moderator:
            return self.Role.MODERATOR
        if self.is_employee:
            return self.Role.EMPLOYEE
        return self.Role.GUEST

    def get_full_name(self) -> str:
        '''
        Возвращает ФИО пользователя.
        '''
        return self.full_name

    def get_short_name(self) -> str:
        '''
        Возвращает Фамилия И.(О). пользователя.
        '''
        return self.short_name

    def __str__(self) -> str:
        return f'{self.role} {self.full_name}, {self.email}, {self.phone_number}'


class Employee(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='employee',
        verbose_name='Пользователь'
    )
    hotel = models.ForeignKey(
        'hotels.Hotel',
        on_delete=models.CASCADE,
        related_name='employees',
        verbose_name='Отель'
    )

    class Meta:
        db_table = 'employee'
        verbose_name = 'Сотрудник'
        verbose_name_plural = 'Сотрудники'

    def __str__(self):
        return str(self.user)


class Moderator(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='moderator',
        verbose_name='Пользователь'
    )

    class Meta:
        db_table = 'moderator'
        verbose_name = 'Модератор'
        verbose_name_plural = 'Модераторы'

    def __str__(self):
        return str(self.user)


class Administrator(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='admin',
        verbose_name='Пользователь'
    )
    is_owner = models.BooleanField(default=False)

    class Meta:
        db_table = 'admin'
        verbose_name = 'Администратор'
        verbose_name_plural = 'Администраторы'

    def __str__(self):
        return str(self.user)
