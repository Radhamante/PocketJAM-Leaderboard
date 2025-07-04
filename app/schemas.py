from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class LeaderboardCreate(BaseModel):
    name: str

class LeaderboardInfo(BaseModel):
    name: str
    created_at: datetime
    total_scores: int
    top_score: Optional[dict]

class LeaderboardKeys(BaseModel):
    leaderboard_id: str
    public_key: str
    admin_key: str

class ScoreCreate(BaseModel):
    player_name: str
    score: int

class ScoreOut(BaseModel):
    rank: int
    player_name: str
    score: int
    submitted_at: datetime
