from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base


DATABASE_URL = "sqlite:///./backend/agent.db"

engine = create_engine(DATABASE_URL, connect_args= {"check_same_thread": False})
SessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)

Base = declarative_base()

class UserProfile(Base):
    __tablename__ = "Profiles"

    id = Column(Integer, primary_key= True, index= True)

    name = Column(String, nullable= False)
    keywords= Column(String, nullable= True)
    industry= Column(Text, nullable= True)

class GeneratedLinkedinPost(Base):
    __tablename__ = "Posts"

    id = Column(Integer, primary_key=True, index=True)

    content = Column(Text, nullable= False)
    scheduled_time = Column(String, nullable= True)


class ScheduledPost(Base):
    __tablename__ = "scheduled_posts"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    scheduled_time = Column(DateTime, nullable=False)


Base.metadata.create_all(bind= engine)

# existing imports and code...
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
