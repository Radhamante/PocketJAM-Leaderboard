import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.sqlite import BLOB
from sqlalchemy.orm import relationship
from .database import Base

class Leaderboard(Base):
    __tablename__ = "leaderboards"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, unique=True, nullable=False)
    public_key = Column(String, unique=True, default=lambda: str(uuid.uuid4()))
    admin_key = Column(String, unique=True, default=lambda: str(uuid.uuid4()))
    created_at = Column(DateTime, default=datetime.utcnow)

    scores = relationship("Score", back_populates="leaderboard", cascade="all, delete-orphan")


class Score(Base):
    __tablename__ = "scores"

    id = Column(Integer, primary_key=True, index=True)
    leaderboard_id = Column(String, ForeignKey("leaderboards.id"), nullable=False)
    player_name = Column(String, nullable=False)
    score = Column(Integer, nullable=False)
    submitted_at = Column(DateTime, default=datetime.utcnow)

    leaderboard = relationship("Leaderboard", back_populates="scores")
