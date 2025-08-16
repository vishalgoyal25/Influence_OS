from sqlalchemy.orm import Session
from backend.database import ScheduledPost

def create_scheduled_post(db: Session, content: str, scheduled_time):

    new_post = ScheduledPost(content=content, scheduled_time=scheduled_time)
    
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

def get_scheduled_posts(db: Session):
    
    return db.query(ScheduledPost).order_by(ScheduledPost.scheduled_time).all()
