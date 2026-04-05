***
В самый первый раз

1. Создать .env (пример — `.env.example`)

2. Инициализировать проект:

***Если бэк***

```bash
docker compose run --rm backend uv run django-admin startproject  < имя > .
```

***Если фронт***

Создать файлы `frontend/src/index.js` и `frontend/public/index.html`

3. Запустить:

```bash
make up
```
***

#### Остановить

```bash
make down
```

Остановить и удалить данные БД:

```bash
make down-v
```
