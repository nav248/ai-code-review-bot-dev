# github_client.py
import os
from dotenv import load_dotenv
import httpx

# Load environment variables
load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
if not GITHUB_TOKEN:
    raise ValueError("⚠️ GITHUB_TOKEN not found. Please set it in your environment or .env file.")

HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json",
}

async def get_changed_files(owner: str, repo: str, pr_number: int):
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/files"
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=HEADERS)
        response.raise_for_status()
        data = response.json()

    files = [
        {
            "filename": f["filename"],
            "status": f["status"],
            "additions": f["additions"],
            "deletions": f["deletions"],
            "changes": f["changes"],
            "patch": f.get("patch", "")
        }
        for f in data
    ]
    return files
import asyncio
from github_client import get_changed_files  # if your script is named github_client.py

# Replace with your repo info
OWNER = "nav248"
REPO = "ai-code-review-bot-dev/actions"
PR_NUMBER = 1  # replace with a real PR number

async def main():
    files = await get_changed_files(OWNER, REPO, PR_NUMBER)
    print("Changed files:", files)

if __name__ == "__main__":
    asyncio.run(main())
