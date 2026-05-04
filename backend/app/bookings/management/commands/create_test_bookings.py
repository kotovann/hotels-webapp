import random
from typing import Any, Optional

from django.db import transaction
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandParser
from faker import Faker

from app.accounts.models import Guest, Moderator
from app.bookings.models import Booking, BookingPayment, Review
from app.bookings.utils.helpers.faker_providers import (
    BookingProvider, BookingPaymentProvider, ReviewProvider
)
from app.hotels.models import Room


User = get_user_model()


class Command(BaseCommand):
    help = 'Генерирует тестовые записи о бронировании'
    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            '--bookings',
            '-b',
            type=int,
            default=10,
            help='Количество бронирований (по умолчанию 10)',
        )
        parser.add_argument(
            '--reviews',
            '-r',
            type=int,
            default=3,
            help='Количество отзывов (по умолчанию 3)',
        )

    def handle(self, *_args: Any, **options: Any) -> Optional[str]:
        bookings_count: int = options.get('bookings')
        reviews_count: int = options.get('reviews')

        faker = Faker('ru_RU')
        rooms = Room.objects.filter(hotel__is_active=True)
        guests = Guest.objects.all()
        if not guests:
            self.stderr.write('Нет пользователей с ролью Гость')
            return
        bookings = self._create_bookings(
            BookingProvider(faker), rooms,
            guests, bookings_count
        )

        if not bookings:
            msg = (
                'Бронирования не были сгенерированы, переданное количество: '
                f'"{bookings_count}".'
            )
            if reviews_count > 0:
                msg += ' Будут взяты существующие.'
            self.stdout.write(self.style.WARNING(msg))
            bookings = Booking.objects.all()
            if not bookings.exists():
                self.stderr.write('Нет доступных бронирований.')
                return
        else:
            self._create_payments(BookingPaymentProvider(faker), bookings)

        moderators = Moderator.objects.all()
        closed_bookings = [
            b for b in bookings
            if b.status == Booking.Status.CLOSED and not hasattr(b, 'review')
        ]
        reviews = self._create_reviews(
            ReviewProvider(faker), closed_bookings,
            moderators, reviews_count
        )

        if not reviews:
            msg = (
                'Отзывы не были сгенерированы, переданное количество: '
                f'"{reviews_count}".'
            )
            self.stdout.write(self.style.WARNING(msg))

    def _create_bookings(
        self, generator: BookingProvider, rooms: list[Room],
        guests: list[User], count: int
    ) -> list[Booking]:
        new_bookings = []

        moved_count = round(count * 0.1)
        cancelled_count = moved_count
        active_count = max((moved_count + cancelled_count + round(count * 0.6)), 1)
        closed_count = count - active_count

        for _ in range(count):
            room = random.choice(rooms)
            guest = random.choice(guests)
            booking_data = generator.booking()
            if not room.is_pets_allowed and booking_data['pets_count'] != 0:
                booking_data['pets_count'] = 0
            if room.bed_count < (booking_data['adults_count'] + booking_data['children_count']):
                booking_data['children_count'] = 0
                if booking_data['adults_count'] > room.bed_count:
                    booking_data['adults_count'] = room.bed_count
            if active_count > 0:
                booking_data['status'] = Booking.Status.ACTIVE
                active_count -= 1
            elif closed_count > 0:
                booking_data['status'] = Booking.Status.CLOSED
                closed_count -= 1
            new_bookings.append(Booking(guest=guest, room=room, **booking_data))

        with transaction.atomic():
            created_bookings = Booking.objects.bulk_create(new_bookings)
            moved_or_cancelled_bookings = random.sample(
                [b for b in created_bookings if b.status == Booking.Status.ACTIVE],
                k=(moved_count + cancelled_count)
            )

            for booking in moved_or_cancelled_bookings:
                if cancelled_count > 0:
                    booking.cancel(generator.cancellation_reason())
                    cancelled_count -= 1
                elif moved_count > 0:
                    new_check_in = generator.check_in_date()
                    new_check_out = generator.check_out_date(new_check_in)
                    booking.move(new_check_in, new_check_out)
                    moved_count -= 1

        for booking in created_bookings:
            self.stdout.write(self.style.SUCCESS(f'Создано {booking}'))

        return created_bookings

    def _create_payments(
        self, generator: BookingPaymentProvider, bookings: list[Booking]
    ) -> list[BookingPayment]:
        new_payments = []

        for booking in bookings:
            payment_data = generator.booking_payment()
            new_payments.append(BookingPayment(booking=booking, **payment_data))

        created_payments = BookingPayment.objects.bulk_create(new_payments)

        for payment in created_payments:
            self.stdout.write(self.style.SUCCESS(f'Создан {payment}'))

        return created_payments

    def _create_reviews(
        self, generator: ReviewProvider, bookings: list[Booking],
        moderators: list[Moderator], count: int
    ) -> list[Review]:
        new_reviews = []

        if count > len(bookings):
            self.stdout.write(self.style.WARNING(
                f'Переданное количество отзывов "{count}" больше, чем '
                f'количество доступных бронирований: {len(bookings)}.'
                'Каждому бронированию будет добавлено по одному отзыву.'
            ))
            count = len(bookings)

        for i in range(count):
            review_data = generator.review()
            if review_data['status'] != Review.Status.DRAFT:
                if not moderators:
                    review_data['status'] = Review.Status.DRAFT
                else:
                    review_data['moderated_by'] = random.choice(moderators)
            new_reviews.append(Review(booking=bookings[i], **review_data))

        created_reviews = Review.objects.bulk_create(new_reviews)

        for review in created_reviews:
            self.stdout.write(self.style.SUCCESS(f'Создан {review}'))

        return created_reviews
