from decimal import Decimal
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone


class BookingStatus(models.TextChoices):
    ACTIVE = 'Активно'
    MOVED = 'Перенесено'
    CANCELLED = 'Отменено'
    CLOSED = 'Завершено'


class PaymentStatus(models.TextChoices):
    NOT_PAYED = 'Не оплачено'
    PAYED = 'Оплачено'


def _calc_total_price(instance) -> Decimal:
    people_count = Decimal(instance.adults_count + instance.children_count)
    room_type = instance.room.room_type
    room_capacity = Decimal(room_type.capacity)
    extra_people_count = max(Decimal(0), people_count - room_capacity)
    base_price = room_type.price_per_night
    extra_pay = room_type.extra_pay_per_person * extra_people_count
    return Decimal(instance.days_count) * (base_price + extra_pay)


class Booking(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='bookings',
        verbose_name='Зарегистрированный пользователь'
    )
    room = models.ForeignKey(
        'hotels.Room',
        on_delete=models.CASCADE,
        related_name='bookings',
        verbose_name='Номер',
    )
    adults_count = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1, message='В брони должен быть хотя бы один взрослый')],
        verbose_name='Количество взрослых',
    )
    children_count = models.PositiveSmallIntegerField(
        verbose_name='Количество детей',
    )
    pets_count = models.PositiveSmallIntegerField(
        verbose_name='Количество животных',
    )
    check_in_date = models.DateField(
        verbose_name='Дата въезда',
    )
    check_out_date = models.DateField(
        verbose_name='Дата выселения',
    )
    status = models.CharField(
        choices=BookingStatus.choices,
        default=BookingStatus.ACTIVE,
        verbose_name='Статус брони',
    )
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        editable=False,
        verbose_name='К оплате',
    )
    payment_status = models.CharField(
        choices=PaymentStatus.choices,
        default=PaymentStatus.NOT_PAYED,
        verbose_name='Статус платежа',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания',
    )
    cancelled_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Дата отмены',
    )
    cancellation_reason = models.CharField(
        max_length=255,
        verbose_name='Причина отмены',
    )

    class Meta:
        db_table = 'booking'
        ordering = [
            '-created_at', 'room__hotel__name',
            'room__floor', 'room__number_on_floor', 'user__last_name'
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(check_out_date__gt=models.F('check_in_date')),
                name='booking_checkout_after_checkin',
                violation_error_message='Дата выезда должна быть позже даты заезда'
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(status=BookingStatus.CANCELLED, cancelled_at__isnull=False) |
                    models.Q(
                        status__in=[BookingStatus.ACTIVE, BookingStatus.CLOSED, BookingStatus.MOVED]
                    )
                ),
                name='booking_cancelled_at_required',
                violation_error_message='При отмене брони необходимо указать дату отмены'
            ),
        ]

    def save(self, *args, **kwargs):
        if not self.pk:  # только при создании
            self.total_price = _calc_total_price(self)
        if self.is_cancelled and not self.cancelled_at:
            self.cancelled_at = timezone.now()
        super().save(*args, **kwargs)

    @property
    def days_count(self) -> int:
        return (self.check_out_date - self.check_in_date).days

    def __str__(self) -> str:
        parts = [
            f'Бронь от {self.created_at}',
            f'Дата заселения: {self.check_in_date}',
            f'Дата выселения: {self.check_out_date}',
            f'К оплате: {self.total_price}',
            f'Статус оплаты: {self.payment_status}',
            f'Статус брони: {self.status}',
        ]
        return ', '.join(parts)


class Review(models.Model):
    booking = models.OneToOneField(
        Booking,
        on_delete=models.CASCADE,
        related_name='review',
        verbose_name='Запись о бронировании',
    )
    rating = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1, message='Минимальная оценка 1 звезда'),
            MaxValueValidator(5, message='Максимальная оценка 5 звезд'),
        ],
        verbose_name='Оценка',
    )
    comment = models.TextField(
        max_length=3072,
        null=True,
        blank=True,
        verbose_name='Комментарий',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания',
    )
    is_published = models.BooleanField(
        default=False,
        verbose_name='Опубликовать',
    )
    published_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Дата публикации',
    )

    class Meta:
        db_table = 'review'
        ordering = ['is_published', '-created_at']
        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(is_published=True, published_at__isnull=False) |
                    models.Q(is_published=False)
                ),
                name='review_published_at_required',
                violation_error_message='При публикации необходимо указать дату публикации'
            ),
        ]
        
    def clean(self):
        if self.booking.status != BookingStatus.CLOSED:
            raise ValidationError('Отзыв можно оставить только на завершённую бронь')
        
    def save(self, *args, **kwargs):
        if self.is_published and not self.published_at:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)
    
    def __str__(self) -> str:
        parts = [
            f'Оценка {self.rating}',
            f'комментарий: {self.comment[:50]}...' if self.comment else 'без комментария',
            f'опубликовано: {self.published_at}' if self.is_published else 'не опубликовано',
            f'относится к брони от {self.booking}',
            f'пользователь: {self.booking.user}'
        ]
        return ', '.join(parts)
