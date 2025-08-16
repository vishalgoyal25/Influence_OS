# FastAPI Routes.

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from pydantic import BaseModel

from backend.database import SessionLocal, get_db 
from backend.crud import create_scheduled_post, get_scheduled_posts


router = APIRouter()

class ScheduledPostRequest(BaseModel):
    content: str
    scheduled_time: datetime

@router.post("/schedulepost")
def schedule_post(request: ScheduledPostRequest, db: Session = Depends(get_db)):
    post = create_scheduled_post(db, request.content, request.scheduled_time)
    return {"message": "Post scheduled", "post": post}

@router.get("/scheduledposts")
def read_scheduled_posts(db: Session = Depends(get_db)):
    posts = get_scheduled_posts(db)
    return posts
