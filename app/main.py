from fastapi import FastAPI, HTTPException, Depends, Request, Header
from sqlalchemy.orm import Session
from typing import List, Optional
from fastapi.middleware.cors import CORSMiddleware

from .database import SessionLocal, engine, Base
from .models import Leaderboard, Score
from .schemas import LeaderboardCreate, LeaderboardKeys, ScoreCreate, ScoreOut, LeaderboardInfo

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Game Jam Scoreboard API")

# CORS pour les jeux web
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/leaderboards/", response_model=LeaderboardKeys)
def create_leaderboard(payload: LeaderboardCreate, db: Session = Depends(get_db)):
    lb = Leaderboard(name=payload.name)
    db.add(lb)
    db.commit()
    db.refresh(lb)
    return LeaderboardKeys(
        leaderboard_id=lb.id,
        public_key=lb.public_key,
        admin_key=lb.admin_key,
    )

@app.post("/leaderboards/{public_key}/scores", status_code=201)
def submit_score(public_key: str, payload: ScoreCreate, db: Session = Depends(get_db)):
    leaderboard = db.query(Leaderboard).filter_by(public_key=public_key).first()
    if not leaderboard:
        raise HTTPException(status_code=404, detail="Leaderboard not found")
    score = Score(
        leaderboard_id=leaderboard.id,
        player_name=payload.player_name,
        score=payload.score
    )
    db.add(score)
    db.commit()
    return {"message": "Score ajouté avec succès"}

@app.get("/leaderboards/{public_key}/scores", response_model=List[ScoreOut])
def get_scores(public_key: str, limit: int = 10, order: str = "desc", db: Session = Depends(get_db)):
    leaderboard = db.query(Leaderboard).filter_by(public_key=public_key).first()
    if not leaderboard:
        raise HTTPException(status_code=404, detail="Leaderboard not found")
    query = db.query(Score).filter_by(leaderboard_id=leaderboard.id)
    scores = query.order_by(Score.score.desc() if order == "desc" else Score.score.asc()).limit(limit).all()
    return [
        ScoreOut(rank=i+1, player_name=s.player_name, score=s.score, submitted_at=s.submitted_at)
        for i, s in enumerate(scores)
    ]

@app.delete("/leaderboards/{leaderboard_id}")
def delete_leaderboard(leaderboard_id: str, x_admin_key: str = Header(...), db: Session = Depends(get_db)):
    leaderboard = db.query(Leaderboard).filter_by(id=leaderboard_id, admin_key=x_admin_key).first()
    if not leaderboard:
        raise HTTPException(status_code=403, detail="Unauthorized")
    db.delete(leaderboard)
    db.commit()
    return {"message": "Leaderboard supprimé"}

@app.delete("/leaderboards/{leaderboard_id}/scores")
def reset_scores(leaderboard_id: str, x_admin_key: str = Header(...), db: Session = Depends(get_db)):
    leaderboard = db.query(Leaderboard).filter_by(id=leaderboard_id, admin_key=x_admin_key).first()
    if not leaderboard:
        raise HTTPException(status_code=403, detail="Unauthorized")
    db.query(Score).filter_by(leaderboard_id=leaderboard_id).delete()
    db.commit()
    return {"message": "Scores effacés"}

@app.get("/leaderboards/{public_key}", response_model=LeaderboardInfo)
def get_leaderboard_info(public_key: str, db: Session = Depends(get_db)):
    leaderboard = db.query(Leaderboard).filter_by(public_key=public_key).first()
    if not leaderboard:
        raise HTTPException(status_code=404, detail="Leaderboard not found")
    scores = leaderboard.scores
    top_score = max(scores, key=lambda s: s.score, default=None)
    return LeaderboardInfo(
        name=leaderboard.name,
        created_at=leaderboard.created_at,
        total_scores=len(scores),
        top_score={
            "player_name": top_score.player_name,
            "score": top_score.score
        } if top_score else None
    )
