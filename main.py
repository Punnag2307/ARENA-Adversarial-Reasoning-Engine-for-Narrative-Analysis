from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import os

from orchestrator import run_arena

app = FastAPI(title="ARENA")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class TickerRequest(BaseModel):
    ticker: str

@app.get("/", response_class=HTMLResponse)
async def root():
    with open("frontend/index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.post("/analyze")
async def analyze(request: TickerRequest):
    """Run full ARENA debate and return results."""
    results = run_arena(request.ticker, export=True)
    if not results:
        return {"error": "Data quality too low for debate"}
    return results

@app.get("/export/{filename}")
async def download_export(filename: str):
    """Download exported debate file."""
    filepath = os.path.join("exports", filename)
    if os.path.exists(filepath):
        return FileResponse(filepath, filename=filename)
    return {"error": "File not found"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)