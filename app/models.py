from sqlalchemy import String, Integer, Float, ForeignKey, UniqueConstraint, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Developer(Base):
    __tablename__ = "developers"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    country: Mapped[str] = mapped_column(String(50), nullable=False)

    games: Mapped[list["Game"]] = relationship(back_populates="developer")


class Game(Base):
    __tablename__ = "games"
    __table_args__ = (UniqueConstraint("title", name="uq_game_title"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    release_year: Mapped[int] = mapped_column(Integer, nullable=False)
    rating: Mapped[float] = mapped_column(Float, nullable=False)  # 0.0 – 10.0

    developer_id: Mapped[int] = mapped_column(ForeignKey("developers.id"), nullable=False)

    developer: Mapped["Developer"] = relationship(back_populates="games")

    achievements: Mapped[list["Achievement"]] = relationship(
        back_populates="game",
        cascade="all, delete-orphan" # при удалении игры автоматически удаляются все её достижения
    )


class Achievement(Base):
    __tablename__ = "achievements"
    __table_args__ = (UniqueConstraint("name", "game_id", name="uq_achievement_per_game"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    points: Mapped[int] = mapped_column(Integer, nullable=False)  # очки за достижение

    # тоже удаляет достижения при удалении игры (на уровне БД)
    game_id: Mapped[int] = mapped_column(ForeignKey("games.id", ondelete="CASCADE"), nullable=False)

    game: Mapped["Game"] = relationship(back_populates="achievements")
