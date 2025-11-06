# backend/app.py

from fastapi import FastAPI, Request

app = FastAPI()

@app.get("/")
def root():
    return {"message": "AI Code Review Bot is running!"}

@app.post("/review")
async def review(request: Request):
    data = await request.json()
    return {"status": "received", "data": data}
