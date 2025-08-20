from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from backend.aiAgent import Generate_Linkedin_Post

app = FastAPI(title="Influence OS AI Inference API")

class InferenceRequest(BaseModel):
    prompt: str = None
    max_length: int = 200
    post_type: str = None
    tone: str = None

@app.post("/generatepost")
def generate_post(request: InferenceRequest):
    try:
        post_content = Generate_Linkedin_Post(
            prompt=request.prompt,
            max_length=request.max_length,
            post_type=request.post_type,
            tone=request.tone,
        )
        return {"generated_post": post_content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def home():
    return {"message": "Welcome to the Influence OS AI Inference API"}
