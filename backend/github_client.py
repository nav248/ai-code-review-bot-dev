import os
import httpx
import asyncio

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
if not GITHUB_TOKEN:
    raise ValueError("⚠️ GITHUB_TOKEN not found. Set it in GitHub Secrets.")

# Read PR number and repo from environment
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

# Mock AI review function
def ai_review_patch(file_patch):
    return f"AI Review: Looks good! (Patch length: {len(file_patch)} characters)"

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
            comments.append(f"**{f['filename']}**:\n{ai_review_patch(f['patch'])}")
        else:
            comments.append(f"**{f['filename']}**:\nNo patch available to review.")

    comment_body = "\n\n".join(comments)
    await post_pr_comment(OWNER, REPO, PR_NUMBER, comment_body)

if __name__ == "__main__":
    asyncio.run(main())
