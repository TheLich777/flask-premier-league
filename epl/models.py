from __future__ import annotations

from epl import db
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, ForeignKey
from typing import List

class Club(db.Model):
    __tablename__ = 'clubs'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    stadium: Mapped[str] = mapped_column(String(100), nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    logo: Mapped[str] = mapped_column(String(200), nullable=False)

    players: Mapped[List["Player"]] = relationship("Player", back_populates="club")

    def __repr__(self) -> str:
        return f"<Club name={self.name}>"

class Player(db.Model):
    __tablename__ = 'players'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)  
    position: Mapped[str] = mapped_column(String(50), nullable=False)
    nationality: Mapped[str] = mapped_column(String(50), nullable=False)
    goal: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    squad_no: Mapped[int] = mapped_column(Integer, nullable=True)
    img: Mapped[str] = mapped_column(String(200), nullable=False)

    club_id: Mapped[int] = mapped_column(ForeignKey("clubs.id"), nullable=False)
    club: Mapped["Club"] = relationship("Club", back_populates="players")

    def __repr__(self) -> str:
        return f"<Player id={self.id} name={self.name} position={self.position} nationality={self.nationality} goal={self.goal} club_id={self.club_id}>"
