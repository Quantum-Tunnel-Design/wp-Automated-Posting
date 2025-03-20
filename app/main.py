from fastapi import FastAPI, HTTPException
import requests
from requests.auth import HTTPBasicAuth
from mangum import Mangum
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from .schemas import BlogRequest
from fastapi.responses import JSONResponse
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Wordpress BlogWriter API", version="1.0")
handler = Mangum(app, lifespan="auto")

load_dotenv()

WORDPRESS_URL = os.getenv('WORDPRESS_URL')
USERNAME = os.getenv('NAME')
PASSWORD = os.getenv('PASSWORD')
BLOG_API_URL = os.getenv('BLOG_API_URL')

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WordPress API endpoint
POST_URL = f"{WORDPRESS_URL}/wp-json/wp/v2/posts"


@app.post("/create-post/")
def create_post(request: BlogRequest):
    ai_data = {
        "topic": request.topic,
        "word_count": request.word_count,
        "background": request.background,
        "keywords": request.keywords,
        "status": "draft"
    }

    logger.info(f"Request to Blog API: {ai_data}")

    ai_response = requests.post(BLOG_API_URL, json=ai_data)

    logger.info(f"AI Response Status: {ai_response.status_code}")
    logger.info(f"AI Response Body: {ai_response.text}")

    if ai_response.status_code == 200:
        try:
            ai_content = ai_response.json().get("blog_content", "")
            if not ai_content:
                raise HTTPException(status_code=422, detail="Failed to generate blog content")
        except Exception as e:
            logger.error(f"Error parsing AI response: {e}")
            raise HTTPException(status_code=422, detail="Failed to parse AI response")
        
        post_data = {
            "title": request.topic,
            "content": ai_content,
            "status": request.status
        }

        response = requests.post(POST_URL, json=post_data, auth=HTTPBasicAuth(USERNAME, PASSWORD), allow_redirects=False)

        if response.status_code == 201:
            return JSONResponse(status_code=200, content={"message": "Blog post created successfully!", "post": response.json()})
        else:
            return JSONResponse(status_code=response.status_code, content={"error": response.text})
    else:
        logger.error(f"Error generating blog content: {ai_response.text}")
        raise HTTPException(status_code=ai_response.status_code, detail="Failed to generate blog content")
