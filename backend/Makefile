# Значения по умолчанию
# Путь к фикстурам
FIXTURES_PATH = fixtures
# Количество пользователей для создания
USER_COUNT = 10
USER_GROUP = 'Гость'
# Данные админа
ADMIN_NAME = 'Adminov Admin'
ADMIN_EMAIL = 'test@admin.com'
ADMIN_PHONE = '89000000000'
ADMIN_PSWD = 'test'
# Параметры удаления пользователей
USER_LOOKUP = 'is_superuser=False,is_staff=False'

# Функции
define dump_to_file
	uv run python manage.py dumpdata --settings=config.settings \
		--indent 2 --format json --output $(FIXTURES_PATH)/$(2).json $(1)
endef

define load_from_file
	uv run python manage.py loaddata $(FIXTURES_PATH)/$(1).json
endef

define docker_dump_to_file
	docker compose exec backend $(call dump_to_file,$(1),$(2))
endef

define docker_load_from_file
	docker compose exec backend $(call load_from_file,$(1))
endef

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
	@echo "замените строку с SECRET_KEY в .env на сгенерированную"

# Тестовые данные
load-data:
	$(call docker_load_from_file,auth_data)
	$(call docker_load_from_file,users_data)

save-data:
	$(call docker_dump_to_file,auth accounts.GroupPriority,auth_data)
	$(call docker_dump_to_file,accounts.User,users_data)

create-admin:
	@echo "Доступны параметры ADMIN_NAME=<ФИО или ФИ>, ADMIN_EMAIL=<email>, ADMIN_PHONE=<8XXXXXXXXXX>, ADMIN_PSWD=<пароль>, ADMIN_GROUP=<название> при вызове create-admin"
	docker compose exec backend uv run python manage.py create_admin --admin-name=$(ADMIN_NAME) \
		--admin-email=$(ADMIN_EMAIL) --admin-phone=$(ADMIN_PHONE) --admin-pswd=$(ADMIN_PSWD)

gen-users:
	@echo "Доступен параметр USER_COUNT=<число>, USER_GROUP=<название> при вызове gen-users"
	docker compose exec backend uv run python manage.py create_test_users --users=$(USER_COUNT)

delete-all-users:
	docker compose exec backend uv run python manage.py delete_users

delete-users:
	@echo "Доступен параметр USER_LOOKUP=<параметр=значение> при вызове delete-users"
	docker compose exec backend uv run python manage.py delete_users --user-lookup=$(USER_LOOKUP)
