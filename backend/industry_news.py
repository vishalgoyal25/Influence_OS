from dotenv import load_dotenv
load_dotenv()
import os
import httpx
from fastapi import APIRouter, Query

router = APIRouter()

NEWS_API_KEY = os.getenv("NEWS_API_KEY")

@router.get("/industry-news")
async def get_industry_news(
    keyword: str = Query(..., description="Industry or topic keyword"),
    page_size: int = Query(5, description="Number of articles to return")
    ):
    
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": keyword,
        "language": "en",
        "sortBy": "relevance",
        "pageSize": page_size,
        "apiKey": NEWS_API_KEY
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        data = response.json()

    if data.get("status") != "ok":
        return {"error": "Failed to fetch news"}

    # Return only key fields to frontend
    articles = [
        {
            "title": article["title"],
            "description": article.get("description"),
            "url": article["url"],
            "source": article["source"]["name"],
            "publishedAt": article["publishedAt"]
        }
        for article in data.get("articles", [])
    ]

    return {"keyword": keyword, "articles": articles}
