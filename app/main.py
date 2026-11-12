from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app import models, schemas

app = FastAPI(title="Game Library API", version="1.0")

@app.get("/health")
def health():
    return {"status": "ok"}

# ================================================== DEVELOPERS ==================================================

@app.get("/developers", response_model=list[schemas.DeveloperOut])
def get_developers(db: Session = Depends(get_db)):
    return db.query(models.Developer).all()


@app.get("/developers/{dev_id}", response_model=schemas.DeveloperOut)
def get_developer(dev_id: int, db: Session = Depends(get_db)):
    dev = db.get(models.Developer, dev_id)
    if not dev:
        raise HTTPException(status_code=404, detail="Developer not found")
    return dev


@app.post("/developers", response_model=schemas.DeveloperOut, status_code=status.HTTP_201_CREATED)
def create_developer(data: schemas.DeveloperCreate, db: Session = Depends(get_db)):
    dev = models.Developer(name=data.name, country=data.country)
    db.add(dev)
    try:
        db.commit()
        db.refresh(dev)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Developer with this name already exists")
    return dev


@app.patch("/developers/{dev_id}", response_model=schemas.DeveloperOut)
def update_developer(dev_id: int, data: schemas.DeveloperUpdate, db: Session = Depends(get_db)):
    dev = db.get(models.Developer, dev_id)
    if not dev:
        raise HTTPException(status_code=404, detail="Developer not found")
    if data.name is not None:
        dev.name = data.name
    if data.country is not None:
        dev.country = data.country
    try:
        db.commit()
        db.refresh(dev)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Developer with this name already exists")
    return dev


@app.delete("/developers/{dev_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_developer(dev_id: int, db: Session = Depends(get_db)):
    dev = db.get(models.Developer, dev_id)
    if not dev:
        raise HTTPException(status_code=404, detail="Developer not found")
    # Бизнес-правило 1: нельзя удалить разработчика, если есть его игры
    if dev.games:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete developer that has games. Remove games first."
        )
    db.delete(dev)
    db.commit()


# ================================================== GAMES ==================================================

@app.get("/games", response_model=list[schemas.GameOut])
def get_games(db: Session = Depends(get_db)):
    return db.query(models.Game).all()


@app.get("/games/{game_id}", response_model=schemas.GameOut)
def get_game(game_id: int, db: Session = Depends(get_db)):
    game = db.get(models.Game, game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    return game


@app.post("/games", response_model=schemas.GameOut, status_code=status.HTTP_201_CREATED)
def create_game(data: schemas.GameCreate, db: Session = Depends(get_db)):
    if not db.get(models.Developer, data.developer_id):
        raise HTTPException(status_code=400, detail="Developer does not exist")

    game = models.Game(
        title=data.title,
        release_year=data.release_year,
        rating=data.rating,
        developer_id=data.developer_id,
    )
    db.add(game)
    try:
        db.commit()
        db.refresh(game)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Game with this title already exists")
    return game


@app.patch("/games/{game_id}", response_model=schemas.GameOut)
def update_game(game_id: int, data: schemas.GameUpdate, db: Session = Depends(get_db)):
    game = db.get(models.Game, game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    if data.developer_id is not None and not db.get(models.Developer, data.developer_id):
        raise HTTPException(status_code=400, detail="Developer does not exist")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(game, field, value)

    try:
        db.commit()
        db.refresh(game)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Game with this title already exists")
    return game


@app.delete("/games/{game_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_game(game_id: int, db: Session = Depends(get_db)):
    game = db.get(models.Game, game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    db.delete(game)
    db.commit()


# ================================================== ACHIEVEMENTS ==================================================

@app.get("/achievements", response_model=list[schemas.AchievementOut])
def get_achievements(db: Session = Depends(get_db)):
    return db.query(models.Achievement).all()


@app.get("/achievements/{ach_id}", response_model=schemas.AchievementOut)
def get_achievement(ach_id: int, db: Session = Depends(get_db)):
    ach = db.get(models.Achievement, ach_id)
    if not ach:
        raise HTTPException(status_code=404, detail="Achievement not found")
    return ach


@app.post("/achievements", response_model=schemas.AchievementOut, status_code=status.HTTP_201_CREATED)
def create_achievement(data: schemas.AchievementCreate, db: Session = Depends(get_db)):
    if not db.get(models.Game, data.game_id):
        raise HTTPException(status_code=400, detail="Game does not exist")

    ach = models.Achievement(
        name=data.name,
        description=data.description,
        points=data.points,
        game_id=data.game_id,
    )
    db.add(ach)
    try:
        db.commit()
        db.refresh(ach)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Achievement with this name already exists in this game")
    return ach


@app.patch("/achievements/{ach_id}", response_model=schemas.AchievementOut)
def update_achievement(ach_id: int, data: schemas.AchievementUpdate, db: Session = Depends(get_db)):
    ach = db.get(models.Achievement, ach_id)
    if not ach:
        raise HTTPException(status_code=404, detail="Achievement not found")

    if data.game_id is not None and not db.get(models.Game, data.game_id):
        raise HTTPException(status_code=400, detail="Game does not exist")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(ach, field, value)

    try:
        db.commit()
        db.refresh(ach)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Achievement with this name already exists in this game")
    return ach


@app.delete("/achievements/{ach_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_achievement(ach_id: int, db: Session = Depends(get_db)):
    ach = db.get(models.Achievement, ach_id)
    if not ach:
        raise HTTPException(status_code=404, detail="Achievement not found")
    db.delete(ach)
    db.commit()
