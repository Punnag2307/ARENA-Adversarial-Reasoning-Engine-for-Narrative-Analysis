def validate_data(data: dict) -> dict:
    """
    Check data quality before debate starts.
    Returns a quality report with warnings and a score.
    """

    warnings = []
    critical_missing = []
    score = 100  # Start perfect, deduct for gaps

    price = data.get("price_data", {})
    fund = data.get("fundamentals", {})
    insider = data.get("insider_activity", {})
    analyst = data.get("analyst_data", {})
    news = data.get("news", [])

    # --- Critical fields (big deductions) ---
    if fund.get("pe_ratio") == "N/A" or not fund.get("pe_ratio"):
        critical_missing.append("P/E Ratio")
        score -= 15

    if fund.get("revenue_growth_yoy") == "N/A" or not fund.get("revenue_growth_yoy"):
        critical_missing.append("Revenue Growth")
        score -= 15

    if fund.get("free_cash_flow") == "N/A" or not fund.get("free_cash_flow"):
        critical_missing.append("Free Cash Flow")
        score -= 10
        warnings.append("FCF missing — agents cannot assess cash generation quality")

    if fund.get("return_on_equity") == "N/A" or not fund.get("return_on_equity"):
        critical_missing.append("Return on Equity")
        score -= 10
        warnings.append("ROE missing — capital efficiency analysis will be limited")

    # --- Important fields (medium deductions) ---
    if analyst.get("consensus_target") == "N/A":
        warnings.append("No analyst consensus target — Street positioning unknown")
        score -= 8

    if not news or len(news) == 0:
        warnings.append("No recent news — sentiment analysis will be limited")
        score -= 7

    if insider.get("insider_activity"):
        warnings.append("Insider transaction data unavailable")
        score -= 5

    # --- Minor fields ---
    if fund.get("debt_to_equity") == "N/A":
        warnings.append("Debt/Equity missing — leverage risk assessment limited")
        score -= 5

    if price.get("beta") == "N/A":
        warnings.append("Beta missing — market risk correlation unknown")
        score -= 5

    # --- Quality rating ---
    if score >= 85:
        quality = "EXCELLENT"
        quality_emoji = "🟢"
    elif score >= 65:
        quality = "GOOD"
        quality_emoji = "🟡"
    elif score >= 45:
        quality = "MODERATE"
        quality_emoji = "🟠"
    else:
        quality = "POOR"
        quality_emoji = "🔴"

    return {
        "score": max(score, 0),
        "quality": quality,
        "quality_emoji": quality_emoji,
        "warnings": warnings,
        "critical_missing": critical_missing,
        "debate_viable": score >= 40,
        "news_count": len(news),
    }


def print_validation_report(report: dict, ticker: str):
    """Print a clean validation report to terminal."""

    print(f"\n{'━'*62}")
    print(f"  DATA QUALITY REPORT — {ticker}")
    print(f"{'━'*62}")
    print(f"  Score:   {report['score']}/100  {report['quality_emoji']} {report['quality']}")
    print(f"  News:    {report['news_count']} headlines found")

    if report['critical_missing']:
        print(f"\n  ⚠️  CRITICAL MISSING:")
        for field in report['critical_missing']:
            print(f"     — {field}")

    if report['warnings']:
        print(f"\n  ℹ️  WARNINGS:")
        for w in report['warnings']:
            print(f"     — {w}")

    if not report['debate_viable']:
        print(f"\n  🔴 DATA TOO SPARSE — debate quality will be severely limited")
        print(f"     Consider trying a different ticker or data source")
    else:
        print(f"\n  ✅ Data sufficient for debate")

    print(f"{'━'*62}\n")