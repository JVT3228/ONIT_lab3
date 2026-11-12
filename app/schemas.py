from pydantic import BaseModel, Field, ConfigDict


# ---------- Developer ----------
class DeveloperCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    country: str = Field(min_length=2, max_length=50)


class DeveloperUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=100)
    country: str | None = Field(default=None, min_length=2, max_length=50)


class DeveloperOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    country: str


# ---------- Game ----------
class GameCreate(BaseModel):
    title: str = Field(min_length=1, max_length=150)
    release_year: int = Field(ge=1970, le=2030)
    rating: float = Field(ge=0.0, le=10.0)
    developer_id: int


class GameUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=150)
    release_year: int | None = Field(default=None, ge=1970, le=2030)
    rating: float | None = Field(default=None, ge=0.0, le=10.0)
    developer_id: int | None = None


class GameOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    release_year: int
    rating: float
    developer_id: int


# ---------- Achievement ----------
class AchievementCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    description: str = Field(min_length=5, max_length=500)
    points: int = Field(ge=1, le=100)
    game_id: int


class AchievementUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=100)
    description: str | None = Field(default=None, min_length=5, max_length=500)
    points: int | None = Field(default=None, ge=1, le=100)
    game_id: int | None = None


class AchievementOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str
    points: int
    game_id: int
