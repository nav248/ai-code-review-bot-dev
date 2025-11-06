import os
import httpx
import asyncio
import openai

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not GITHUB_TOKEN or not OPENAI_API_KEY:
    raise ValueError("⚠️ GITHUB_TOKEN or OPENAI_API_KEY not found in environment variables.")

openai.api_key = OPENAI_API_KEY

# Read PR number and repo from environment (set by workflow)
PR_NUMBER = int(os.getenv("PR_NUMBER"))
REPO_FULL = os.getenv("REPO")  # format: "owner/repo"
OWNER, REPO = REPO_FULL.split("/")

HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json",
}

async def get_changed_files(owner: str, repo: str, pr_number: int):
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/files"
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=HEADERS)
        response.raise_for_status()
        data = response.json()

    files = []
    for f in data:
        files.append({
            "filename": f["filename"],
            "status": f["status"],
            "additions": f["additions"],
            "deletions": f["deletions"],
            "changes": f["changes"],
            "patch": f.get("patch", "")
        })
    return files

async def ai_review_patch(file_patch):
    """Call OpenAI GPT to generate a code review"""
    if not file_patch.strip():
        return "No changes to review."

    prompt = f"Please review the following code changes and provide constructive feedback:\n\n{file_patch}"
    
    response = await openai.ChatCompletion.acreate(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=300
    )
    review = response.choices[0].message.content
    return review

async def post_pr_comment(owner: str, repo: str, pr_number: int, body: str):
    url = f"https://api.github.com/repos/{owner}/{repo}/issues/{pr_number}/comments"
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=HEADERS, json={"body": body})
        response.raise_for_status()
    print(f"✅ Comment posted successfully to PR #{pr_number}")

async def main():
    files = await get_changed_files(OWNER, REPO, PR_NUMBER)
    print("Changed files:", files)

    comments = []
    for f in files:
        if f["patch"]:
            review = await ai_review_patch(f["patch"])
            comments.append(f"**{f['filename']}**:\n{review}")
        else:
            comments.append(f"**{f['filename']}**:\nNo patch available to review.")

    comment_body = "\n\n".join(comments)
    await post_pr_comment(OWNER, REPO, PR_NUMBER, comment_body)

if __name__ == "__main__":
    asyncio.run(main())
