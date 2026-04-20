# ARENA
### Adversarial Reasoning Engine for Narrative Analysis

> *Five analysts. One stock. No consensus.*

ARENA is a multi-agent financial debate system that takes any stock ticker and generates a structured adversarial debate between five AI analysts — each with a distinct mental model, blind spot, and voice. It's not one AI opinion. It's a room full of disagreeing experts.

---

## What It Does

You enter a ticker. Five analysts read the same Goldman-style financial briefing and argue about it.

**The Analysts:**
| Analyst | Role | Mental Model | Blind Spot |
|---|---|---|---|
| Marcus | Permabull | TAM, moats, compounding | Valuation multiples |
| Elena | Short Seller | Forensic accounting, risk signals | Being too early |
| Dev | Behavioral Economist | Market psychology, anchoring bias | Ex-post rationalization |
| Zara | Quant Purist | Factor models, statistical edges | Narrative regime changes |
| Rohan | First-Year Analyst | Consensus, Street targets | Almost everything |

After two rounds of cross-examination, a Moderator synthesizes the debate into a probability-weighted verdict and surfaces the single most important unanswered question.

---

## Demo

```
ARENA — ETERNAL.NS (Eternal Limited)
Data Quality: GOOD (75/100) | Temperature: CONTESTED | Polarization: HIGHLY POLARIZED

MARCUS  +0.900  ████████████████████
ELENA   -0.875  ████████████████████
ZARA    -0.800  ████████████████
DEV     -0.450  █████████
ROHAN   +0.225  ████

VERDICT — Bull: 25% | Base: 50% | Bear: 25%

Unanswered: "If management truly believes in this inflection, why has insider
buying remained at exactly zero over 90 days while the stock trades 26% below
its high?"
```

---

## Architecture

```
User Input (ticker)
        ↓
Data Fetcher (yfinance + Alpha Vantage + SEC EDGAR)
        ↓
Data Validator → Quality Score + Warnings
        ↓
Context Builder → Goldman-style Briefing
        ↓
Round 1: 5 Persona Agents (parallel, independent views)
        ↓
Round 2: Cross-examination (each agent reads all prior responses)
        ↓
Claude-based Conflict Scorer → Sentiment scores + Drift detection
        ↓
Synthesizer Agent → Probability verdict + Unanswered question
        ↓
FastAPI → Bloomberg-style Web UI
```

---

## Tech Stack

| Layer | Tool |
|---|---|
| LLM | Anthropic Claude (claude-opus-4-5) |
| Financial Data | yfinance, Alpha Vantage, SEC EDGAR |
| Orchestration | Python, custom multi-agent loop |
| Conflict Scoring | Claude-based stance evaluation |
| Backend | FastAPI + Uvicorn |
| Frontend | Vanilla HTML/CSS/JS, Chart.js |
| PDF Export | ReportLab |
| Visualization | Chart.js (donut, radar) |

---

## Features

- **Multi-agent debate** — 5 persona agents with distinct system prompts, mental models, and enforced blind spots
- **2-round cross-examination** — agents read and respond to each other's arguments
- **Hallucination guard** — agents can only cite numbers that appear in the briefing
- **Drift prevention** — non-negotiable persona rules prevent agents converging to consensus
- **Claude-based conflict scoring** — accurate sentiment detection regardless of word choice
- **Drift detection** — tracks whether agents changed position between rounds
- **Data quality validation** — scores briefing completeness and warns before debate starts
- **What-If simulation** — change key variables and see how the verdict shifts
- **PDF export** — professional research report format
- **Ticker search** — autocomplete search by company name or symbol
- **Indian stock support** — append `.NS` (NSE) or `.BO` (BSE) for Indian markets

---

## Setup

### Prerequisites
- Python 3.10+
- Anthropic API key
- Alpha Vantage API key

### Installation

```bash
git clone https://github.com/yourusername/ARENA.git
cd ARENA

python -m venv venv
venv\Scripts\activate       # Windows
source venv/bin/activate    # Mac/Linux

pip install -r requirements.txt
```

### Configuration

Create a `.env` file in the root directory:

```
ANTHROPIC_API_KEY=your_anthropic_key_here
ALPHA_VANTAGE_KEY=your_alpha_vantage_key_here
```

### Run

```bash
python app.py
```

Open your browser at `http://localhost:8000`

---

## Usage

1. Type a company name or ticker in the search box (e.g. "Apple", "NVDA", "Reliance")
2. Select from the dropdown
3. Click **INITIATE DEBATE**
4. Wait 2-3 minutes while all 5 agents debate in real time
5. Read the full debate, analyze conflict scores, run What-If simulations
6. Export as PDF

**Indian stocks:** Search by name (e.g. "Reliance Industries") or type ticker directly with suffix (e.g. `RELIANCE.NS`)

---

## Project Structure

```
ARENA/
├── agents/
│   ├── base_agent.py        # Base class with hallucination guard + drift prevention
│   ├── permabull.py         # Marcus — long-only growth investor
│   ├── short_seller.py      # Elena — forensic short seller
│   ├── behavioral.py        # Dev — behavioral economist
│   ├── quant.py             # Zara — systematic quant
│   ├── first_year.py        # Rohan — first-year analyst
│   └── synthesizer.py       # Moderator — neutral synthesis
├── data/
│   ├── fetcher.py           # Financial data pipeline
│   ├── context_builder.py   # Goldman-style briefing builder
│   ├── validator.py         # Data quality scoring
│   ├── conflict_scorer.py   # Claude-based sentiment analysis
│   ├── exporter.py          # Text export
│   └── pdf_exporter.py      # PDF report generation
├── static/
│   └── index.html           # Bloomberg-style frontend
├── orchestrator.py          # Full debate pipeline
├── app.py                   # FastAPI server
├── config.py                # Configuration
├── .env                     # API keys (never committed)
└── requirements.txt
```

---

## Sample Output

**On NVDA (high data quality, bullish lean):**
- Marcus: +0.92 — "Dominant infrastructure for next decade of compute"
- Elena: -0.71 — "Insider selling $340M in 90 days is not a footnote"
- Dev: -0.38 — "Retail is so long NVDA that any disappointment triggers forced liquidation"
- Zara: +0.44 — "Momentum factor positive, earnings revision trend upward"
- Rohan: +0.31 — "Consensus target implies 18% upside but... the insider thing"

**On ETERNAL.NS (missing data, contested):**
- Marcus: +0.90 — "Blinkit break-even is the proof point skeptics demanded"
- Elena: -0.88 — "83.3% earnings growth from a trailing P/E of 1010 is arithmetic, not progress"
- Zara: -0.80 — "Without FCF and ROE, any valuation is fiction. Pass."
- Polarization index: 1.775 — Highly polarized

---

## What Makes This Different

Most AI finance tools give you one answer. ARENA gives you five ways of being wrong — and lets them argue.

The debate architecture encodes five distinct schools of finance thought into agents that genuinely disagree. The cross-examination mechanism forces agents to engage with each other's specific arguments. The Claude-based conflict scorer measures actual stance, not word frequency.

This is not a sentiment analyzer. It's a thinking system that mirrors how markets debate truth.

---

## License

MIT License — use freely, attribution appreciated.

---

*"The bears are missing the forest for the trees." — Marcus, always*
