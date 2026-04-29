# Значения по умолчанию
# Путь к фикстурам
FIXTURES_PATH = fixtures
# Тестовые пользователи
GUEST_ROLE_NAME = 'Гость'
EMPLOYEE_ROLE_NAME = 'Сотрудник'
MOD_ROLE_NAME = 'Модератор'
ADMIN_ROLE_NAME = 'Администратор'
USER_COUNT = 10
ROLE_NAME = $(GUEST_ROLE_NAME)
# Параметры удаления пользователей
USER_LOOKUP = 'employee__is_null=True'
# Тестовые отели
HOTEL_NAME = 'ИмяСетиОтелей'
HOTEL_COUNT = 7
ROOM_TYPE_COUNT = 15
ROOM_PER_HOTEL = 20
WITHOUT_PHOTO = ''
# Параметры удаления отелей
HOTEL_LOOKUP = ''
ROOM_TYPE_LOOKUP = ''
# Тестовые бронирования
BOOKING_COUNT = 15
REVIEW_COUNT = 5
# Параметры удаления бронирований
BOOKING_LOOKUP = ''

# Функции
define dump_to_file
	uv run python manage.py dumpdata --settings=config.settings \
		--indent 2 --format json --output $(FIXTURES_PATH)/$(2).json $(1)
endef

define load_from_file
	uv run python manage.py loaddata $(FIXTURES_PATH)/$(1).json
endef

define docker_dump_to_file
	$(call dump_to_file,$(1),$(2))
endef

define docker_load_from_file
	docker compose exec backend $(call load_from_file,$(1))
endef

define create_group
	docker compose exec backend uv run python manage.py create_group --name=$(1) --priority=$(2)
endef

list-commands:
	@echo Доступные make-команды:
	@echo   migrate                     - Применить миграции
	@echo   shell                       - Запустить Django shell
	@echo   superuser                   - Создать администратора
	@echo   test                        - Запустить pytest
	@echo   lint                        - Проверить код ruff
	@echo   lint-fix                    - Исправить ошибки ruff
	@echo   gen-secret                  - Сгенерировать SECRET_KEY
	@echo   load-data                   - Загрузить фикстуры
	@echo   save-data                   - Сохранить фикстуры
	@echo   gen-users                   - Сгенерировать тестовых пользователей
	@echo   delete-all-users            - Удалить всех пользователей
	@echo   delete-users                - Удалить пользователей по фильтру
	@echo   create-hotels               - Сгенерировать тестовые отели
	@echo   create-hotels-without-photo - Сгенерировать отели без фото
	@echo   delete-hotels               - Удалить отели по фильтру
	@echo   delete-room-types           - Удалить типы номеров по фильтру
	@echo   delete-hotels-all           - Удалить все отели и типы номеров
	@echo   create-bookings             - Сгенерировать бронирования
	@echo   delete-bookings-all         - Удалить все бронирования и отзывы
	@echo   list-commands               - Показать эту справку

migrate:
	docker compose exec backend uv run python manage.py makemigrations
	docker compose exec backend uv run python manage.py migrate

shell:
	docker compose exec backend uv run python manage.py shell

superuser:
	docker compose exec backend uv run python manage.py createsuperuser

test:
	docker compose exec backend uv run pytest

lint:
	docker compose exec backend uv run ruff check .

lint-fix:
	docker compose exec backend uv run ruff check --fix .

gen-secret:
	docker compose exec backend uv run python -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(32))"
	@echo "Замените строку с SECRET_KEY в .env на сгенерированную"

# Тестовые данные
load-data:
	$(call docker_load_from_file,hotels_data)
	$(call docker_load_from_file,users_data)
	$(call docker_load_from_file,bookings_data)

save-data:
	$(call docker_dump_to_file,hotels,hotels_data)
	$(call docker_dump_to_file,accounts.User,users_data)
	$(call docker_dump_to_file,bookings,bookings_data)

## Пользователи
create-guests:
	@echo "Доступен параметр USER_COUNT=<число>"
	docker compose exec backend uv run python manage.py create_test_users --users $(USER_COUNT) --role $(GUEST_ROLE_NAME)

create-employees:
	@echo "Доступны параметры USER_COUNT=<число>, HOTEL_ID=<число>"
	docker compose exec backend uv run python manage.py create_test_users --users $(USER_COUNT) --role $(EMPLOYEE_ROLE_NAME) --hotel_id $(HOTEL_ID)

create-moderators:
	@echo "Доступен параметр USER_COUNT=<число>"
	docker compose exec backend uv run python manage.py create_test_users --users $(USER_COUNT) --role $(MOD_ROLE_NAME)

create-users:
	@echo "Доступны параметры USER_COUNT=<число>, ROLE_NAME=<роль>"
	@echo "Роли:"
	docker compose exec backend uv run python manage.py create_test_users --role --help
	docker compose exec backend uv run python manage.py create_test_users --users $(USER_COUNT) --role $(ROLE_NAME)

gen-users: USER_COUNT=20 create-guests USER_COUNT=10 create-employees USER_COUNT=3 create-moderators

delete-all-users:
	docker compose exec backend uv run python manage.py delete_users

delete-users:
	@echo "Доступен параметр USER_LOOKUP=<параметр=значение> при вызове delete-users"
	docker compose exec backend uv run python manage.py delete_users --user-lookup $(USER_LOOKUP)

## Отели
create-hotels:
	@echo "Доступны параметры HOTEL_NAME=<название сети> HOTEL_COUNT=<число> ROOM_TYPE_COUNT=<число> ROOM_PER_HOTEL=<число> WITHOUT_PHOTO='--without-photo'"
	docker compose exec backend uv run python manage.py create_test_hotels --name $(HOTEL_NAME) \
		--hotel-count $(HOTEL_COUNT) --room-type-count $(ROOM_TYPE_COUNT) --room-per-hotel $(ROOM_PER_HOTEL) $(WITHOUT_PHOTO)

create-room-types:
	@echo "Доступны параметры HOTEL_NAME=<название сети> ROOM_TYPE_COUNT=<число>"
	docker compose exec backend uv run python manage.py create_test_hotels --name $(HOTEL_NAME) \
		--hotel-count 0 --room-type-count $(ROOM_TYPE_COUNT) --room-per-hotel 0

create-rooms:
	@echo "Доступны параметры HOTEL_NAME=<название сети> ROOM_PER_HOTEL=<число> WITHOUT_PHOTO='--without-photo'"
	docker compose exec backend uv run python manage.py create_test_hotels --name=$(HOTEL_NAME) \
		--hotel-count=0 --room-type-count=0 --room-per-hotel=$(ROOM_PER_HOTEL)$(WITHOUT_PHOTO)

delete-hotels:
	@echo "Доступен параметр HOTEL_LOOKUP=<параметр=значение>"
	docker compose exec backend uv run python manage.py delete_hotels --hotel-lookup=$(HOTEL_LOOKUP)

delete-room-types:
	@echo "Доступен параметр ROOM_TYPE_LOOKUP=<параметр=значение>"
	docker compose exec backend uv run python manage.py delete_room_types --room-type-lookup=$(ROOM_TYPE_LOOKUP)

delete-hotels-all: delete-hotels delete-room-types

# Бронирование
create-bookings:
	@echo "Доступны параметры BOOKING_COUNT=<число> REVIEW_COUNT=<число>"
	docker compose exec backend uv run python manage.py create_test_bookings \
		--bookings=$(BOOKING_COUNT) --reviews=$(REVIEW_COUNT)

delete-bookings-all:
	@echo "Доступен параметр BOOKING_LOOKUP=<параметр=значение>"
	docker compose exec backend uv run python manage.py delete_bookings --booking-lookup=$(BOOKING_LOOKUP)
