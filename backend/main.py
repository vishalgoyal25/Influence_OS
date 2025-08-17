from dotenv import load_dotenv
load_dotenv()

import os
from fastapi import FastAPI
from pydantic import BaseModel

from backend.database import SessionLocal, GeneratedLinkedinPost
from backend.aiAgent import Generate_Linkedin_Post
from backend import linkedin_api

from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import UserProfile, get_db

app = FastAPI(title="Linkedin AI Agent API", version="1.0")

# Add session middleware for OAuth token storage
app.add_middleware(SessionMiddleware,
                   secret_key=os.environ.get("SESSION_SECRET_KEY", "supersecret"))


# Add CORS middleware for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5500"
    ],
    allow_credentials= True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include LinkedIn OAuth routes with prefix '/linkedin'
app.include_router(linkedin_api.router, prefix="/linkedin")


from typing import Optional
class PromptRequest(BaseModel):
    prompt: Optional[str] = None
    max_length: int = 200
    post_type: str = None
    tone: str = None

    # Add profile info fields optional to accept frontend data if sent
    name: str = ""
    keywords: str = ""
    industry: str = ""

@app.get("/")
def home():
    return {"message": "Welcome to the LinkedIn AI Agent API"}

@app.post("/generatepost")
def GeneratePost(request: PromptRequest, db: Session = Depends(get_db)):

    # Fetch profile from DB if not provided in request
    if not (request.name and request.keywords and request.industry):
        profile = db.query(UserProfile).filter(UserProfile.id == 1).first()
        if profile:
            name = profile.name
            keywords = profile.keywords or ""
            industry = profile.industry or ""
        else:
            name, keywords, industry = "", "", ""
    else:
        name = request.name
        keywords = request.keywords
        industry = request.industry

    # Build enhanced prompt including profile info
    details = []
    if request.post_type:
        details.append(f"Post Type: {request.post_type}.")
    if request.tone:
        details.append(f"Tone: {request.tone}.")
    if name:
        details.append(f"User Name: {name}.")
    if industry:
        details.append(f"Industry: {industry}.")
    if keywords:
        details.append(f"Keywords/Skills: {keywords}.")

    full_prompt = "Generate a LinkedIn post."
    if details:
        full_prompt += " " + " ".join(details)
    if request.prompt:
        full_prompt += f" Topic/Context: {request.prompt}"
    
    # Generate post with AI
    post_content= Generate_Linkedin_Post(prompt=full_prompt,
                                        max_length=request.max_length,
                                        post_type=request.post_type,
                                        tone=request.tone)

    return {"Prompt": request.prompt,
            "PostType":request.post_type,
            "Tone":request.tone,
            
            "Name": name,
            "Keywords": keywords,
            "Industry": industry,
            "Generated Post": post_content }


@app.get("/getposts")
def GetPosts():
    db= SessionLocal()
    posts = db.query(GeneratedLinkedinPost).all()

    db.close()

    return [{"ID":p.id, "CONTENT":p.content, "SCHEDULE_TIME":p.scheduled_time} 
            for p in posts]


# Including LinkedIn Post API routes
from backend.linkedin_post import router as linkedin_post_router
app.include_router(linkedin_post_router)

# Including Industry_News API routes
from backend.industry_news import router as industry_news_router
app.include_router(industry_news_router)

# Including Content Calender API routes
from backend.content_calendar import router as content_calendar_router
app.include_router(content_calendar_router)




class ProfileInput(BaseModel):
    name: str
    keywords: str = ""
    industry: str = ""

@app.post("/profile")
def save_profile(profile: ProfileInput, db: Session = Depends(get_db)):
    # Always update/insert profile with id = 1 (single user version)
    existing = db.query(UserProfile).filter(UserProfile.id == 1).first()
    if existing:
        existing.name = profile.name
        existing.keywords = profile.keywords
        existing.industry = profile.industry
    else:
        new_profile = UserProfile(id=1, name=profile.name, keywords=profile.keywords, industry=profile.industry)
        db.add(new_profile)
    db.commit()
    return {"message": "Profile saved"}

@app.get("/profile")
def get_profile(db: Session = Depends(get_db)):
    profile = db.query(UserProfile).filter(UserProfile.id == 1).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return {
        "name": profile.name,
        "keywords": profile.keywords,
        "industry": profile.industry
    }
