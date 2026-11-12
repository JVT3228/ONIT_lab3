import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db
from app import models


# ---------- Тестовая БД в памяти (SQLite) ----------
SQLALCHEMY_DATABASE_URL = "sqlite://"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


# ==================== 5 UNIT-тестов ====================

def test_create_developer():
    r = client.post("/developers", json={"name": "Valve", "country": "USA"})
    assert r.status_code == 201
    assert r.json()["name"] == "Valve"


def test_create_duplicate_developer():
    client.post("/developers", json={"name": "Valve", "country": "USA"})
    r = client.post("/developers", json={"name": "Valve", "country": "USA"})
    assert r.status_code == 400


def test_get_nonexistent_game():
    r = client.get("/games/999")
    assert r.status_code == 404


def test_rating_validation():
    d = client.post("/developers", json={"name": "CDPR", "country": "Poland"}).json()
    r = client.post("/games", json={
        "title": "Test Game",
        "release_year": 2020,
        "rating": 15.0,  # > 10 — ошибка
        "developer_id": d["id"],
    })
    assert r.status_code == 422


def test_delete_game_cascades_achievements():
    """Как в Steam: удалили игру → достижения тоже исчезли"""
    d = client.post("/developers", json={"name": "FromSoftware", "country": "Japan"}).json()
    g = client.post("/games", json={
        "title": "Elden Ring",
        "release_year": 2022,
        "rating": 9.5,
        "developer_id": d["id"],
    }).json()
    client.post("/achievements", json={
        "name": "Elden Lord",
        "description": "Become the Elden Lord",
        "points": 50,
        "game_id": g["id"],
    })
    # Удаляем игру
    r = client.delete(f"/games/{g['id']}")
    assert r.status_code == 204
    # Достижений больше нет
    r = client.get("/achievements")
    assert r.status_code == 200
    assert len(r.json()) == 0


# ==================== 3 INTEGRATION-теста ====================

def test_full_developer_crud():
    r = client.post("/developers", json={"name": "Nintendo", "country": "Japan"})
    assert r.status_code == 201
    did = r.json()["id"]

    r = client.get(f"/developers/{did}")
    assert r.status_code == 200

    r = client.patch(f"/developers/{did}", json={"country": "Japan / Kyoto"})
    assert r.status_code == 200
    assert "Kyoto" in r.json()["country"]

    r = client.delete(f"/developers/{did}")
    assert r.status_code == 204


def test_full_game_and_achievement_flow():
    d = client.post("/developers", json={"name": "CD Projekt", "country": "Poland"}).json()

    r = client.post("/games", json={
        "title": "The Witcher 3",
        "release_year": 2015,
        "rating": 9.8,
        "developer_id": d["id"],
    })
    assert r.status_code == 201
    game_id = r.json()["id"]

    r = client.post("/achievements", json={
        "name": "Friends in Black Robes",
        "description": "Complete the main quest",
        "points": 30,
        "game_id": game_id,
    })
    assert r.status_code == 201

    r = client.get("/achievements")
    assert r.status_code == 200
    assert len(r.json()) == 1

    r = client.delete(f"/achievements/{r.json()[0]['id']}")
    assert r.status_code == 204

    r = client.delete(f"/games/{game_id}")
    assert r.status_code == 204


def test_cannot_create_achievement_for_nonexistent_game():
    r = client.post("/achievements", json={
        "name": "Fake",
        "description": "Does not exist",
        "points": 10,
        "game_id": 999,
    })
    assert r.status_code == 400
