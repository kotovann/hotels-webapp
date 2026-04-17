from typing import Optional

from django.db import models
from django.contrib.auth.models import AbstractUser, Group as BaseGroup

from phonenumber_field.modelfields import PhoneNumberField
from app.accounts.managers import UserManager


class GroupPriority(models.Model):
    '''
    Модель приоритета группы пользователей.
    '''
    group = models.OneToOneField(
        BaseGroup,
        verbose_name='Группа пользователей',
        on_delete=models.CASCADE,
        related_name='group_priority',
    )
    priority = models.SmallIntegerField(
        verbose_name='Приоритет группы'
    )

    class Meta:
        verbose_name = 'Приоритет группы пользователей'
        verbose_name_plural = 'Приоритеты групп пользователей'
        ordering = ['-priority']

    def delete(self, *args, **kwargs):
        deleted_priority = self.priority
        super().delete(*args, **kwargs)
        GroupPriority.objects.filter(priority__gt=deleted_priority) \
            .update(priority=models.F('priority') - 1)

    def __str__(self):
        return f'Группа {self.group.name}: приоритет {self.priority}'


class Group(BaseGroup):
    '''
    Прокси-модель Group, добавляющая verbose_name и приоритет.
    '''
    class Meta:
        proxy = True
        verbose_name = 'Группа пользователей'
        verbose_name_plural = 'Группы пользователей'
        ordering = ['name']

    @property
    def priority(self):
        return self.group_priority.priority

    def __str__(self):
        return self.name


class User(AbstractUser):
    '''
    Кастомная модель пользователя, наследующая AbstractUser.
    В качестве идентификатора используется email, поле username отключено.
    '''
    NO_ROLE = 'Нет роли'

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
    def primary_group(self) -> Optional[Group]:
        '''
        Возвращает основную группу пользователя.
        '''
        groups = list(self.groups.select_related('group_priority'))
        if not groups:
            return None
        return min(groups, key=lambda g: g.group_priority.priority)

    @property
    def role(self) -> str:
        '''
        Возвращает основную роль пользователя.
        '''
        return self.primary_group.name if self.primary_group else User.NO_ROLE

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
        return (
            f'Пользователь pk {self.pk}: {self.short_name}, '
            f'почта {self.email}, телефон {self.phone_number}, '
            f'роль: {self.role}'
        )
