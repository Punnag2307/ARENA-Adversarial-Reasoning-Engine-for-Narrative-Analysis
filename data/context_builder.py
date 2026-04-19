def format_number(value, prefix="", suffix="", billions=False):
    """Format large numbers cleanly."""
    if value == "N/A" or value is None:
        return "N/A"
    try:
        value = float(value)
        if billions:
            return f"{prefix}{value/1e9:.2f}B{suffix}"
        if value > 1e9:
            return f"{prefix}{value/1e9:.2f}B{suffix}"
        if value > 1e6:
            return f"{prefix}{value/1e6:.2f}M{suffix}"
        return f"{prefix}{value:.2f}{suffix}"
    except:
        return str(value)


def format_pct(value):
    """Format percentage values."""
    if value == "N/A" or value is None:
        return "N/A"
    try:
        v = float(value)
        # yfinance returns ratios like 0.22 for 22%
        if -1 < v < 1:
            v = v * 100
        return f"{v:.1f}%"
    except:
        return str(value)



def build_context(data: dict) -> str:
    """
    Build a Goldman Sachs-style analyst briefing from raw fetched data.
    This is the document every persona agent will read before speaking.
    """

    ticker = data["ticker"]
    ts = data["timestamp"]
    price = data["price_data"]
    fund = data["fundamentals"]
    insider = data["insider_activity"]
    analyst = data["analyst_data"]
    news = data["news"]

    company_name = fund.get("company_name", ticker)
    sector = fund.get("sector", "N/A")
    industry = fund.get("industry", "N/A")

    # Currency detection
    if ticker.endswith(".NS") or ticker.endswith(".BO"):
        currency = "₹"
    else:
        currency = "$"

    briefing = f"""
╔══════════════════════════════════════════════════════════════╗
   ARENA ANALYST BRIEFING — {ticker} ({company_name})
   Generated: {ts}
╚══════════════════════════════════════════════════════════════╝

SECTOR: {sector} | INDUSTRY: {industry}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. PRICE & MARKET DATA
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Current Price:      {currency}{price.get('current_price', 'N/A')}
6M Price Change:    {price.get('price_change_6m_pct', 'N/A')}%
52W High:           {currency}{price.get('week_52_high', 'N/A')}
52W Low:            {currency}{price.get('week_52_low', 'N/A')}
Market Cap:         {format_number(price.get('market_cap'))}
Beta:               {price.get('beta', 'N/A')}
Avg Volume (30D):   {format_number(price.get('avg_volume_30d'))}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
2. VALUATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Trailing P/E:       {fund.get('pe_ratio', 'N/A')}
Forward P/E:        {fund.get('forward_pe', 'N/A')}
Price/Sales:        {fund.get('price_to_sales', 'N/A')}
Price/Book:         {fund.get('price_to_book', 'N/A')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
3. GROWTH & PROFITABILITY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Revenue Growth YoY: {format_pct(fund.get('revenue_growth_yoy'))}
Earnings Growth:    {format_pct(fund.get('earnings_growth_yoy'))}
Gross Margin:       {format_pct(fund.get('gross_margin'))}
Operating Margin:   {format_pct(fund.get('operating_margin'))}
Return on Equity:   {format_pct(fund.get('return_on_equity'))}
Free Cash Flow:     {format_number(fund.get('free_cash_flow'))}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
4. RISK SIGNALS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Debt/Equity:        {fund.get('debt_to_equity', 'N/A')}
Beta:               {price.get('beta', 'N/A')}
Insider Bought:     {format_number(insider.get('total_bought_90d', 0))} (last 90D)
Insider Sold:       {format_number(insider.get('total_sold_90d', 0))} (last 90D)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
5. ANALYST CONSENSUS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Consensus Target:   {currency}{analyst.get('consensus_target', 'N/A')}
Implied Upside:     {analyst.get('implied_upside_pct', 'N/A')}%
Recent Ratings:     {analyst.get('recent_ratings', 'N/A')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
6. RECENT NEWS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""

    if news:
        for i, item in enumerate(news[:6], 1):
            briefing += f"\n[{i}] {item['title']} — {item['publisher']}"
    else:
        briefing += "\nNo recent news available."

    briefing += f"""

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
7. COMPANY SNAPSHOT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{fund.get('description', 'N/A')}

══════════════════════════════════════════════════════════════
END OF BRIEFING — ARENA v1.0
══════════════════════════════════════════════════════════════
"""
    return briefing