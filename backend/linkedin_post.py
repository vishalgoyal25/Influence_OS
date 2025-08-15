from fastapi import APIRouter, Request, HTTPException
import requests

router = APIRouter()

def get_linkedin_urn(access_token: str):
    url = "https://api.linkedin.com/v2/me"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return None
    data = response.json()
    return data.get("id")


def make_post_payload(author_urn: str, post_text: str):
    return {
        "author": f"urn:li:person:{author_urn}",
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {
                    "text": post_text
                },
                "shareMediaCategory": "NONE"
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        }
    }


def post_to_linkedin(access_token: str, author_urn: str, post_text: str):
    url = "https://api.linkedin.com/v2/ugcPosts"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0"
    }
    payload = make_post_payload(author_urn, post_text)
    response = requests.post(url, headers=headers, json=payload)
    return response


@router.post("/linkedin/post")
async def linkedin_post(request: Request):
    session = request.session
    access_token = session.get("token", {}).get("access_token")
    if not access_token:
        raise HTTPException(status_code=401, detail="User not authenticated with LinkedIn")

    data = await request.json()
    post_text = data.get("text", "")
    if not post_text:
        raise HTTPException(status_code=400, detail="Post text cannot be empty")

    author_urn = get_linkedin_urn(access_token)
    if not author_urn:
        raise HTTPException(status_code=400, detail="Failed to retrieve LinkedIn profile information")

    response = post_to_linkedin(access_token, author_urn, post_text)
    if response.status_code != 201:
        # Forward LinkedIn API error details
        raise HTTPException(status_code=response.status_code, detail=response.json())

    return {"message": "Post successfully published on LinkedIn", "response": response.json()}
