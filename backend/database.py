from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.orm import sessionmaker, declarative_base


DATABASE_URL = "sqlite:///./agent.db"

engine = create_engine(DATABASE_URL, connect_args= {"check_same_thread": False})
sessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)

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
    schedule_time = Column(String, nullable= True)


Base.metadata.create_all(bind= engine)