import os
from datetime import datetime


def export_debate(results: dict, conflict: dict, validation: dict) -> str:
    """
    Export the full ARENA debate session to a text file.
    Returns the filepath of the saved file.
    """

    ticker = results["ticker"]
    company = results["company_name"]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"ARENA_{ticker}_{timestamp}.txt"

    # Create exports folder if it doesn't exist
    os.makedirs("exports", exist_ok=True)
    filepath = os.path.join("exports", filename)

    lines = []

    # Header
    lines.append("=" * 70)
    lines.append(f"  ARENA — ANALYST DEBATE SESSION")
    lines.append(f"  Ticker: {ticker} ({company})")
    lines.append(f"  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append("=" * 70)

    # Data quality
    lines.append(f"\nDATA QUALITY: {validation['quality_emoji']} {validation['quality']} ({validation['score']}/100)")
    if validation['warnings']:
        for w in validation['warnings']:
            lines.append(f"  ⚠ {w}")

    # Conflict summary
    lines.append(f"\nDEBATE TEMPERATURE: {conflict['temperature_emoji']} {conflict['debate_temperature']}")
    lines.append(f"POLARIZATION: {conflict['polarization_emoji']} {conflict['polarization_label']}")
    lines.append(f"DOMINANT VOICE: {conflict['dominant_voice']}")

    # Briefing
    lines.append("\n" + "=" * 70)
    lines.append("  FINANCIAL BRIEFING")
    lines.append("=" * 70)
    lines.append(results["briefing"])

    # Round 1
    lines.append("\n" + "=" * 70)
    lines.append("  ROUND 1 — OPENING POSITIONS")
    lines.append("=" * 70)
    for entry in results["round1"]:
        lines.append(f"\n{'─'*50}")
        lines.append(f"  {entry['agent'].upper()}")
        lines.append(f"{'─'*50}")
        lines.append(entry["response"])

    # Round 2
    lines.append("\n" + "=" * 70)
    lines.append("  ROUND 2 — CROSS EXAMINATION")
    lines.append("=" * 70)
    for entry in results["round2"]:
        lines.append(f"\n{'─'*50}")
        lines.append(f"  {entry['agent'].upper()}")
        lines.append(f"{'─'*50}")
        lines.append(entry["response"])

    # Conflict scores
    lines.append("\n" + "=" * 70)
    lines.append("  CONFLICT ANALYSIS")
    lines.append("=" * 70)
    lines.append(f"\nAgent Sentiment Scores (-1 bearish → +1 bullish):")
    for agent, score in conflict["agent_scores"].items():
        lines.append(f"  {agent:<30} {score:+.3f}")

    lines.append(f"\nDrift Detection:")
    for agent, d in conflict["drift"].items():
        drifted = "DRIFTED" if d["drifted"] else "Stable"
        lines.append(f"  {agent:<30} R1:{d['r1']:+.2f} → R2:{d['r2']:+.2f}  {drifted}")

    # Synthesis
    lines.append("\n" + "=" * 70)
    lines.append("  FINAL SYNTHESIS")
    lines.append("=" * 70)
    lines.append(f"\n{results['synthesis']}")

    lines.append("\n" + "=" * 70)
    lines.append("  END OF ARENA SESSION")
    lines.append("=" * 70)

    # Write file
    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return filepath