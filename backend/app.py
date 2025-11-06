from fastapi import FastAPI
from dotenv import load_dotenv
import os
from backend.github_client import get_changed_files

load_dotenv()

app = FastAPI()

@app.get("/")
def root():
    return {"message": "AI Code Review Bot is running!"}

@app.get("/test-pr")
async def test_pr():
    files = await get_changed_files("nav248", "ai-code-review-bot-dev", 1)
    return files
