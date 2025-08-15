from dotenv import load_dotenv
load_dotenv()

import os
print("CLIENT_ID from env:", os.environ.get("LINKEDIN_CLIENT_ID"))

from fastapi import FastAPI
from pydantic import BaseModel

from backend.database import sessionLocal, GeneratedLinkedinPost
from backend.aiAgent import Generate_Linkedin_Post
from backend import linkedin_api

from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

app = FastAPI(title="Linkedin AI Agent API", version="1.0")

# Add session middleware for OAuth token storage
app.add_middleware(SessionMiddleware,
                   secret_key=os.environ.get("SESSION_SECRET_KEY", "supersecret"))

# Include LinkedIn OAuth routes with prefix '/linkedin'
app.include_router(linkedin_api.router, prefix="/linkedin")


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


from typing import Optional
class PromptRequest(BaseModel):
    prompt: Optional[str] = None
    max_length: int = 200

@app.get("/")
def home():
    return {"message": "Welcome to the LinkedIn AI Agent API"}

@app.post("/generatepost")
def GeneratePost(request: PromptRequest):
    post_content= Generate_Linkedin_Post(request.prompt, request.max_length)

    return {"Prompt": request.prompt, "Generated Post": post_content }


@app.get("/getposts")
def GetPosts():
    db= sessionLocal()
    posts = db.query(GeneratedLinkedinPost).all()

    db.close()

    return [{"ID":p.id, "CONTENT":p.content, "SCHEDULE_TIME":p.schedule_time} 
            for p in posts]
