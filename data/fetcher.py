import yfinance as yf
import requests
import pandas as pd
from datetime import datetime, timedelta
from config import ALPHA_VANTAGE_KEY


def get_price_data(ticker: str) -> dict:
    """Pull price history, volume, and basic stats."""
    stock = yf.Ticker(ticker)
    hist = stock.history(period="6mo")
    info = stock.info

    if hist.empty:
        return {"error": f"No price data found for {ticker}"}

    current_price = hist["Close"].iloc[-1]
    price_6m_ago = hist["Close"].iloc[0]
    price_change_6m = ((current_price - price_6m_ago) / price_6m_ago) * 100

    # 52 week high/low
    hist_1y = stock.history(period="1y")
    week_52_high = hist_1y["Close"].max()
    week_52_low = hist_1y["Close"].min()

    return {
        "current_price": round(current_price, 2),
        "price_change_6m_pct": round(price_change_6m, 2),
        "week_52_high": round(week_52_high, 2),
        "week_52_low": round(week_52_low, 2),
        "avg_volume_30d": int(hist["Volume"].tail(30).mean()),
        "market_cap": info.get("marketCap", "N/A"),
        "beta": info.get("beta", "N/A"),
    }


def get_fundamentals(ticker: str) -> dict:
    """Pull key fundamental metrics."""
    stock = yf.Ticker(ticker)
    info = stock.info

    return {
        "pe_ratio": info.get("trailingPE", "N/A"),
        "forward_pe": info.get("forwardPE", "N/A"),
        "price_to_sales": info.get("priceToSalesTrailing12Months", "N/A"),
        "price_to_book": info.get("priceToBook", "N/A"),
        "revenue_growth_yoy": info.get("revenueGrowth", "N/A"),
        "earnings_growth_yoy": info.get("earningsGrowth", "N/A"),
        "gross_margin": info.get("grossMargins", "N/A"),
        "operating_margin": info.get("operatingMargins", "N/A"),
        "debt_to_equity": info.get("debtToEquity", "N/A"),
        "free_cash_flow": info.get("freeCashflow", "N/A"),
        "return_on_equity": info.get("returnOnEquity", "N/A"),
        "dividend_yield": info.get("dividendYield", "N/A"),
        "sector": info.get("sector", "N/A"),
        "industry": info.get("industry", "N/A"),
        "company_name": info.get("longName", ticker),
        "description": info.get("longBusinessSummary", "N/A")[:300],
    }


def get_insider_activity(ticker: str) -> dict:
    """Pull insider buying/selling activity."""
    stock = yf.Ticker(ticker)

    try:
        insider_df = stock.insider_transactions
        if insider_df is None or insider_df.empty:
            return {"insider_activity": "No recent insider data available"}

        # Last 90 days
        insider_df = insider_df.head(10)
        total_bought = insider_df[insider_df["Shares"] > 0]["Value"].sum()
        total_sold = insider_df[insider_df["Shares"] < 0]["Value"].sum()

        recent = []
        for _, row in insider_df.head(5).iterrows():
            recent.append({
                "insider": row.get("Insider Trading", "Unknown"),
                "transaction": "BUY" if row.get("Shares", 0) > 0 else "SELL",
                "value": row.get("Value", "N/A"),
            })

        return {
            "total_bought_90d": round(float(total_bought), 2) if total_bought else 0,
            "total_sold_90d": round(float(abs(total_sold)), 2) if total_sold else 0,
            "recent_transactions": recent,
        }
    except Exception as e:
        return {"insider_activity": f"Could not fetch insider data: {str(e)}"}


def get_analyst_data(ticker: str) -> dict:
    """Pull analyst recommendations and price targets."""
    stock = yf.Ticker(ticker)

    try:
        info = stock.info

        target_price = info.get("targetMeanPrice") or info.get("targetMedianPrice")
        current_price = info.get("currentPrice") or info.get("regularMarketPrice")

        upside = "N/A"
        if target_price and current_price:
            upside = round(
                ((float(target_price) - float(current_price)) / float(current_price)) * 100, 2
            )

        # Ratings from info directly
        buy_count = info.get("recommendationMean", "N/A")
        rec_key = info.get("recommendationKey", "N/A")

        return {
            "consensus_target": target_price or "N/A",
            "implied_upside_pct": upside,
            "recommendation": rec_key,
            "recommendation_score": buy_count,
            "recent_ratings": f"Consensus: {rec_key} (score: {buy_count}/5)",
        }
    except Exception as e:
        return {
            "consensus_target": "N/A",
            "implied_upside_pct": "N/A",
            "recommendation": "N/A",
            "recommendation_score": "N/A",
            "recent_ratings": "N/A",
        }

def get_news(ticker: str) -> list:
    """Pull recent news headlines."""
    stock = yf.Ticker(ticker)

    try:
        news = stock.news
        if not news:
            return []

        headlines = []
        for item in news[:8]:
            # Handle both old and new yfinance news structure
            if isinstance(item, dict):
                # New structure has nested 'content'
                content = item.get("content", {})
                title = (
                    content.get("title")
                    or item.get("title")
                    or "No title"
                )
                publisher = (
                    content.get("provider", {}).get("displayName")
                    or item.get("publisher")
                    or "Unknown"
                )
            else:
                title = "No title"
                publisher = "Unknown"

            if title and title != "No title":
                headlines.append({
                    "title": title,
                    "publisher": publisher,
                })

        return headlines
    except Exception as e:
        return []


def fetch_all(ticker: str) -> dict:
    """Master function — pulls everything for a ticker."""
    print(f"Fetching data for {ticker}...")

    data = {
        "ticker": ticker.upper(),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "price_data": get_price_data(ticker),
        "fundamentals": get_fundamentals(ticker),
        "insider_activity": get_insider_activity(ticker),
        "analyst_data": get_analyst_data(ticker),
        "news": get_news(ticker),
    }

    print(f"Data fetch complete for {ticker}")
    return data