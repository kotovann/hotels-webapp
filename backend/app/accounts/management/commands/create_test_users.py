import random
from typing import Any, Optional

from django.db import transaction
from django.core.management.base import BaseCommand, CommandParser
from faker import Faker

from app.accounts.models import User, Employee, Moderator, Administrator
from app.hotels.models import Hotel
from utils.normalizers import normalize_email, normalize_phone
from utils.validators import validate_email, validate_phone


fake = Faker('ru_RU')


class Command(BaseCommand):
    help = 'Генерирует тестовых пользователей с разными ролями'

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            '--users',
            '-u',
            type=int,
            default=5,
            help='Количество пользователей для создания (по умолчанию 5)'
        )
        parser.add_argument(
            '--role',
            '-r',
            type=str,
            choices=(User.Role.GUEST, User.Role.EMPLOYEE, User.Role.MODERATOR, User.Role.ADMIN),
            default=User.Role.GUEST,
            help='Роль создаваемых пользователей (по умолчанию Гость)'
        )
        parser.add_argument(
            '--hotel-id',
            type=int,
            help='ID отеля для роли Сотрудник'
        )

    def handle(self, *_args: Any, **options: Any) -> Optional[str]:
        user_count: int = options['users']
        role: str = options['role']
        hotel_id: Optional[int] = options.get('hotel_id')

        hotels = []
        if role == User.Role.EMPLOYEE:
            if hotel_id is not None:
                try:
                    hotels.append(Hotel.objects.get(id=hotel_id))
                except Hotel.DoesNotExist:
                    self.stderr.write(f'Отель с id "{hotel_id}" не найден.')
                    return
            else:
                hotels = list(Hotel.objects.all())
            if not hotels:
                self.stderr.write('Не удалось создать сотрудников: нет доступных отелей.')
                return

        self._create_users(user_count, role, hotels)
        return None

    def _create_users(self, user_count: int, role: str, hotels: list[Hotel]) -> None:
        existing_emails = set(User.objects.values_list('email', flat=True))
        existing_phones = set(User.objects.values_list('phone_number', flat=True))
        new_users = []
        roles = []

        password = 'qwert543'

        for _ in range(user_count):
            email = normalize_email(fake.email())
            while email in existing_emails or not validate_email(email):
                email = normalize_email(fake.email())
            existing_emails.add(email)

            phone = normalize_phone(fake.phone_number())
            while phone in existing_phones or not validate_phone(phone):
                phone = normalize_phone(fake.phone_number())
            existing_phones.add(phone)

            gender = random.choice(['male', 'female'])
            if gender == 'male':
                first_name = fake.first_name_male()
                middle_name = fake.middle_name_male()
                last_name = fake.last_name_male()
            else:
                first_name = fake.first_name_female()
                middle_name = fake.middle_name_female()
                last_name = fake.last_name_female()

            date_of_birth = fake.date_of_birth(minimum_age=18)

            user = User(
                email=email,
                phone_number=phone,
                first_name=first_name,
                middle_name=middle_name,
                last_name=last_name,
                date_of_birth=date_of_birth,
            )
            user.set_password(password)
            new_users.append(user)

        with transaction.atomic():
            created_users = User.objects.bulk_create(new_users)

            for user in created_users:
                if role == User.Role.EMPLOYEE:
                    hotel = random.choice(hotels)
                    roles.append(Employee(user=user, hotel=hotel))
                elif role == User.Role.MODERATOR:
                    roles.append(Moderator(user=user))
                elif role in (User.Role.ADMIN, User.Role.OWNER):
                    is_owner = role == User.Role.OWNER
                    roles.append(Administrator(user=user, is_owner=is_owner))

            if role == User.Role.EMPLOYEE:
                Employee.objects.bulk_create(roles)
            elif role == User.Role.MODERATOR:
                Moderator.objects.bulk_create(roles)
            elif role in (User.Role.ADMIN, User.Role.OWNER):
                Administrator.objects.bulk_create(roles)

        for user in created_users:
            extra_info = ''
            if role == User.Role.EMPLOYEE:
                extra_info = f', отель {hotel.name}'

            self.stdout.write(self.style.SUCCESS(
                f'Создан пользователь: {user.full_name}, email: {user.email}, '
                f'телефон: {user.phone_number}, дата рождения: {user.date_of_birth}, '
                f'роль: {role}{extra_info}, пароль: {password}'
            ))
