from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator, FileExtensionValidator
from django.core.exceptions import ValidationError
from phonenumber_field.modelfields import PhoneNumberField


class Hotel(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Название отеля',
    )
    phone_number = PhoneNumberField(
        null=False,
        blank=False,
        unique=True,
        error_messages={'invalid': 'Введен некорректный номер телефона'},
        verbose_name='Номер телефона',
    )
    email = models.EmailField(
        max_length=100,
        unique=True,
        error_messages={'invalid': 'Введен некорректный email'},
        verbose_name='Email-адрес',
    )
    country = models.CharField(
        max_length=100,
        verbose_name='Страна',
    )
    city = models.CharField(
        max_length=100,
        verbose_name='Город',
    )
    address = models.CharField(
        max_length=255,
        verbose_name='Адрес',
    )
    is_active = models.BooleanField(
        default=False,
        verbose_name='Активен',
    )

    class Meta:
        db_table = 'hotel'
        verbose_name = 'Отель'
        verbose_name_plural = 'Отели'
        ordering = ['is_active', 'country', 'city', 'name']

    def __str__(self) -> str:
        parts = [
            f'Отель {self.name}',
            f'номер телефона: {self.phone}',
            f'email: {self.email}',
            f'адрес: {self.address}',
            self.city,
            self.country,
            f'Состояние: {"работает" if self.is_active else "закрыт"}'
        ]
        return ', '.join(parts)


class RoomType(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Название типа',
    )
    description = models.TextField(
        verbose_name='Описание',
    )
    size = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(2, message='Номер должен быть размером хотя бы 2 кв. м.')],
        verbose_name='Площадь',
        help_text='в квадратных метрах',
    )
    capacity = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1, message='Номер должен вмещать хотя бы одного человека')],
        verbose_name='Вместимость',
    )
    bedroom_count = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1, message='Номер должен иметь хотя бы одно спальное место')],
        verbose_name='Количество спален',
    )
    bathroom_count = models.PositiveSmallIntegerField(
        default=0,
        validators=[MinValueValidator(0, message='Количество ванных не может быть меньше нуля')],
        verbose_name='Количество ванных комнат',
    )
    has_balcony = models.BooleanField(
        default=False,
        verbose_name='Есть балкон',
    )

    class Meta:
        db_table = 'room_type'
        verbose_name = 'Тип номера'
        verbose_name_plural = 'Типы номеров'
        ordering = ['name', '-capacity', '-size']
    
    def __str__(self) -> str:
        parts = [
            f'Тип комнаты: {self.name}',
            f'Размер: {self.size}',
            f'Вместимость: {self.capacity} человек',
        ]
        return ', '.join(parts)


class Room(models.Model):
    hotel = models.ForeignKey(
        'hotels.Hotel',
        on_delete=models.CASCADE,
        related_name='rooms',
    )
    room_type = models.ForeignKey(
        'hotels.RoomType',
        on_delete=models.CASCADE,
        related_name='rooms',
    )
    is_pets_allowed = models.BooleanField(
        default=False,
        verbose_name='Можно с животными',
    )
    is_smoking_allowed = models.BooleanField(
        default=False,
        verbose_name='Можно курить',
    )
    price_per_night = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0, message='Цена не может быть меньше нуля')],
        verbose_name='Цена за ночь',
    )
    extra_pay_per_person = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0, message='Цена не может быть меньше нуля')],
        verbose_name='Доплата за дополнительного человека',
    )
    floor = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1, message='Этаж не может быть меньше 1'),
            MaxValueValidator(100, message='Этаж не может быть больше 100'),
        ],
        verbose_name='Номер этажа',
    )
    number_on_floor = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1, message='Минимальный порядковый номер комнаты равен 1'),
            MaxValueValidator(99, message='Максимальный порядковый номер комнаты равен 99'),
        ],
        verbose_name='Порядковый номер на этаже',
    )
    variant = models.CharField(
        max_length=1,
        null=True,
        blank=True, 
        validators=[RegexValidator(
            regex=r'^[A-Z]$',
            message='Вариация может быть только латинской буквой в высшем регистре',
        )],
        verbose_name='Вариация номера',
        help_text='Например, 1A и 1B (указать только букву)',
    )

    class Meta:
        db_table = 'room'
        verbose_name = 'Номер'
        verbose_name_plural = 'Номера'
        ordering = ['hotel__name', 'room_type__name', 'floor', 'number_on_floor', 'variant', '-price_per_night']
        constraints = [
            models.UniqueConstraint(
                fields=('hotel', 'floor'),
                name='unique_floor_per_hotel',
                violation_error_message='В отеле этаж с таких номером может быть только один',
            ),
            models.UniqueConstraint(
                fields=('hotel', 'floor', 'number_on_floor', 'variant'),
                name='unique_room_per_hotel',
                violation_error_message='В отеле может быть только одна комната'
                'с таким номером и вариантом на этаже'
            )
        ]

    @property
    def room_number(self) -> str:
        return f'{100 * self.floor + self.number_on_floor}{self.variant if self.variant else ""}'

    def __str__(self) -> str:
        parts = [
            f'Номер: {self.room_number}',
            f'этаж: {self.floor}',
            f'отель: {str(self.room_type.hotel)}'
        ]
        return ', '.join(parts)


def _photo_path(instance, filename) -> str:
    return f'rooms/{instance.room.room_type.hotel_id}/{instance.room_id}/{filename}'


class RoomPhoto(models.Model):
    room = models.ForeignKey(
        'hotels.Room',
        on_delete=models.CASCADE,
        related_name='photos',
    )
    photo_path = models.ImageField(
        upload_to=_photo_path,
        validators=[
            FileExtensionValidator(allowed_extensions=['png', 'jpg', 'jpeg', 'webp'],  message='Формат файла не поддерживается')
        ],
        verbose_name='Путь к фото',
    )
    sort_order_number = models.PositiveSmallIntegerField(
        verbose_name='Порядковый номер',
    )
    
    class Meta:
        db_table = 'room_photo'
        verbose_name = 'Фото номера'
        verbose_name_plural = 'Фото номеров'
        ordering = ['room__hotel__name', 'room__floor', 'room__number_on_floor', 'room__variant', 'sort_order_number']
        constraints = [
            models.UniqueConstraint(
                fields=['room', 'sort_order_number'],
                name='unique_order_number_per_room',
                violation_error_message='Уже существует фото комнаты с таким порядковым номером',
            )
        ]

    def __str__(self) -> str:
        return f'Фото №{self.sort_order_number} комнаты {self.room}'
