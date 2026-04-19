from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from orchestrator import run_arena
from data.pdf_exporter import build_pdf
import uvicorn
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

# In-memory store of last debate result
last_debate_result = {}

@app.get("/")
def root():
    return FileResponse("static/index.html")

class TickerRequest(BaseModel):
    ticker: str

@app.post("/api/debate")
def run_debate(req: TickerRequest):
    global last_debate_result
    results = run_arena(req.ticker)
    if not results:
        return {"error": "Debate failed — data quality too low"}

    # Store for export
    last_debate_result = results

    return {
        "ticker": results["ticker"],
        "company_name": results["company_name"],
        "briefing": results["briefing"],
        "round1": results["round1"],
        "round2": results["round2"],
        "synthesis": results["synthesis"],
        "validation": results["validation"],
        "conflict": results["conflict"],
    }

@app.get("/api/search")
def search_ticker(q: str):
    if not q or len(q) < 2:
        return {"results": []}
    try:
        import requests
        url = f"https://query2.finance.yahoo.com/v1/finance/search?q={q}&quotesCount=8&newsCount=0&listsCount=0"
        headers = {'User-Agent': 'Mozilla/5.0'}
        resp = requests.get(url, headers=headers, timeout=5)
        data = resp.json()
        quotes = data.get('quotes', [])
        results = []
        for item in quotes:
            symbol = item.get('symbol', '')
            name = item.get('longname') or item.get('shortname') or symbol
            exchange = item.get('exchange', '')
            qtype = item.get('quoteType', '')
            if qtype in ['EQUITY', 'ETF']:
                results.append({
                    'symbol': symbol,
                    'name': name,
                    'exchange': exchange,
                    'type': qtype
                })
        return {"results": results[:8]}
    except Exception as e:
        return {"results": [], "error": str(e)}

        
@app.post("/api/export")
def export_pdf():
    global last_debate_result
    if not last_debate_result:
        return {"error": "No debate to export — run a debate first"}
    try:
        filepath = build_pdf(
            last_debate_result,
            last_debate_result["conflict"],
            last_debate_result["validation"]
        )
        return FileResponse(
            path=filepath,
            filename=os.path.basename(filepath),
            media_type='application/pdf'
        )
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import webbrowser
    import threading
    def open_browser():
        import time
        time.sleep(1.5)
        webbrowser.open("http://localhost:8000")
    threading.Thread(target=open_browser).start()
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)