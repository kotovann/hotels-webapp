from django.db import models
from django.contrib.auth.models import AbstractUser, Group
from phonenumber_field.modelfields import PhoneNumberField
from app.accounts.managers import UserManager


class User(AbstractUser):
    '''
    Кастомная модель пользователя, наследующая AbstractUser.
    В качестве идентификатора используется email, поле username отключено.
    '''

    username = None
    email = models.EmailField(
        max_length=100,
        unique=True,
        error_messages={'invalid': 'Введен некорректный email.'},
        verbose_name='Электронная почта.',
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
    primary_group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Основная группа',
        help_text='Группа, определяющая основную роль пользователя в системе.',
        related_name='primary_members'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'phone_number']
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
        names = [self.first_name, self.middle_name, self.last_name]
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
    def role(self) -> str:
        '''
        Возвращает основную роль пользователя.
        '''
        return self.primary_group.name if self.primary_group else 'Нет группы'

    def get_full_name(self) -> str:
        return self.full_name

    def get_short_name(self) -> str:
        return self.short_name

    def __str__(self) -> str:
        return f'Пользователь {self.full_name}, роль в системе: {self.role}'
