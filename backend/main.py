from fastapi import FastAPI
from pydantic import BaseModel

from database import sessionLocal, GeneratedLinkedinPost
from aiAgent import Generate_Linkedin_Post


app = FastAPI(title="Linkedin Ai Agent API", version="1.0")

class PromptRequest(BaseModel):
    prompt : str | None = None
    max_length : int = 200

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

