from collections import OrderedDict
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Optional

from faker import Faker
from faker.providers import BaseProvider

from app.bookings.models import Booking, BookingPayment, Review


class BookingProvider(BaseProvider):
    '''Кастомный Faker-провайдер для генерации данных модели Booking'''

    def __init__(self, generator: Faker):
        super().__init__(generator)
        self._type_choices = Booking.Type.values
        self._status_choices = Booking.Status.values

    def adults_count(self) -> int:
        return self.generator.random_int(min=1, max=10)

    def children_count(self) -> int:
        return self.generator.random_int(min=0, max=5)

    def pets_count(self) -> int:
        return self.generator.random_int(min=0, max=3)

    def check_in_date(self, later_than: Optional[datetime]=None) -> date:
        if later_than is None:
            return self.generator.date_this_year()
        days = self.generator.random_int(min=1, max=30)
        return later_than + timedelta(days=days)

    def check_out_date(self, later_than: Optional[datetime]=None) -> date:
        if later_than is None:
            return self.generator.date_this_year()
        days = self.generator.random_int(min=1, max=30)
        return later_than + timedelta(days=days)

    def status(self) -> str:
        return self.generator.random_element(self._status_choices)

    def type(self) -> str:
        return self.generator.random_element(self._type_choices)

    def created_at(self) -> datetime:
        return self.generator.date_time_this_year()

    def cancelled_at(
        self, created_at: Optional[datetime]=None,
        check_in_date: Optional[datetime]=None,
    ) -> Optional[datetime]:
        return self.generator.date_time_between_dates(
            datetime_start=created_at, datetime_end=check_in_date
        )

    def cancellation_reason(self) -> str:
        return self.generator.text(max_nb_chars=255)

    def booking(self) -> dict:
        created_at = self.created_at()
        check_in_date = self.check_in_date(created_at)
        check_out_date = self.check_out_date(check_in_date)
        status = self.status()
        return {
            'adults_count': self.adults_count(),
            'children_count': self.children_count(),
            'pets_count': self.pets_count(),
            'check_in_date': check_in_date,
            'check_out_date': check_out_date,
            'status': status,
            'type': self.type(),
            'created_at': created_at,
        }


class BookingPaymentProvider(BaseProvider):
    '''Кастомный Faker-провайдер для генерации данных модели Review'''

    def __init__(self, generator: Faker):
        super().__init__(generator)
        self._status_choices = BookingPayment.Status.values
        self._purpose_choices = BookingPayment.Purpose.values

    def status(self) -> str:
        return self.generator.random_element(self._status_choices)

    def amount(self) -> Decimal:
        return Decimal(self.generator.random_int(min=300, max=30000))

    def purpose(self) -> str:
        return self.generator.random_element(self._purpose_choices)

    def created_at(self) -> datetime:
        return self.generator.date_time_this_year()

    def paid_at(self, later_than: Optional[datetime]=None) -> datetime:
        if later_than is None:
            return self.generator.date_time_this_year()
        days = self.generator.random_int(min=1, max=7)
        return later_than + timedelta(days=days)

    def booking_payment(self) -> dict:
        created_at = self.created_at()
        return {
            'status': self.status(),
            'amount': self.amount(),
            'purpose': self.purpose(),
            'created_at': created_at,
            'paid_at': self.paid_at(created_at),
        }


class ReviewProvider(BaseProvider):
    '''Кастомный Faker-провайдер для генерации данных модели Review'''

    def __init__(self, generator: Faker):
        super().__init__(generator)
        self._status_choices = OrderedDict([
            (Review.Status.PUBLISHED, 0.35),
            (Review.Status.DRAFT, 0.3),
            (Review.Status.ON_MODERATION, 0.2),
            (Review.Status.REJECTED, 0.1),
            (Review.Status.ARCHIVED, 0.05),
        ])
        self._rating_choices = OrderedDict([
            (5, 0.5),
            (4, 0.25),
            (3, 0.1),
            (2, 0.15)
        ])

    def rating(self) -> int:
        return self.generator.random_element(self._rating_choices)

    def comment(self) -> str:
        return self.generator.text(max_nb_chars=3072)

    def created_at(self) -> datetime:
        return self.generator.date_time_this_year()

    def status(self) -> str:
        return self.generator.random_element(self._status_choices)

    def rejection_reason(self) -> str:
        return self.generator.text(max_nb_chars=255)

    def published_at(self, later_than: Optional[datetime]=None) -> datetime:
        if later_than is not None:
            return later_than + timedelta(days=self.generator.random_int(min=1, max=7))
        return self.generator.date_time_this_year()

    def review(self) -> dict:
        created_at = self.created_at()
        status = self.status()
        published_at = None
        rejection_reason = None
        if status == Review.Status.PUBLISHED:
            published_at = self.published_at(created_at)
        if status == Review.Status.REJECTED:
            rejection_reason = self.rejection_reason()
        return {
            'rating': self.rating(),
            'comment': self.comment(),
            'created_at': created_at,
            'status': status,
            'rejection_reason': rejection_reason,
            'published_at': published_at,
        }
