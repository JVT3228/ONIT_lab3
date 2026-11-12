# Game Library API (ЛР №1 + №2)

REST API библиотеки игр + достижения.

**3 сущности:** Developer → Game → Achievement

## Стек
- FastAPI + SQLAlchemy 2 + Alembic
- PostgreSQL
- Docker + Docker Compose

---

## Запуск через Docker (рекомендуется)

```bash
docker compose up --build
```

После запуска:
- API: http://localhost:8000/docs
- База: PostgreSQL на порту 5432 (внутри сети Docker)

### Полезные команды

| Действие                    | Команда                          |
|-----------------------------|----------------------------------|
| Запуск                      | `docker compose up --build`      |
| Остановка                   | `docker compose down`            |
| Остановка + удаление volume | `docker compose down -v`         |
| Логи                        | `docker compose logs -f`         |

> **Важно:** после `docker compose down` данные **сохраняются** (volume `pgdata`).  
> Чтобы полностью очистить базу — вам придётся воспользоваться командой `docker compose down -v`.

---

## Локальный запуск (без Docker)

1. Создайте БД `games_db`
2. Скопируйте `.env.example` → `.env` , также можно одной командой `cd .env.example .env`
3. `pip install -r requirements.txt`
4. `alembic upgrade head`
5. `uvicorn app.main:app --reload`

---

## Тесты
```bash
pytest -v
```

## Эндпоинты (15)

- `/developers` — CRUD
- `/games` — CRUD
- `/achievements` — CRUD

## Бизнес-правила (надеюсь это они)
1. Нельзя удалить Developer, если у него есть игры.
2. При удалении Game все Achievement удаляются каскадно.
