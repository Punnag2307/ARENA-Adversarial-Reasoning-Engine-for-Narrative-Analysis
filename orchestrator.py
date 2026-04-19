from data.fetcher import fetch_all
from data.context_builder import build_context
from data.validator import validate_data, print_validation_report
from data.conflict_scorer import compute_conflict_score, print_conflict_report
from data.exporter import export_debate
from agents.permabull import Permabull
from agents.quant import Quant
from agents.behavioral import Behavioral
from agents.short_seller import ShortSeller
from agents.first_year import FirstYear
from agents.synthesizer import Synthesizer


def run_arena(ticker: str, export: bool = True) -> dict:
    """Full ARENA debate pipeline with all fixes integrated."""

    print(f"\n{'='*62}")
    print(f"  ARENA — Initiating debate on {ticker.upper()}")
    print(f"{'='*62}\n")

    # Step 1 — Fetch data
    print("📊 Fetching market data...")
    data = fetch_all(ticker)
    briefing = build_context(data)

    # Step 2 — Validate data quality
    validation = validate_data(data)
    print_validation_report(validation, ticker)

    if not validation["debate_viable"]:
        print("🔴 Aborting — data quality too low for meaningful debate.")
        return {}

    # Step 3 — Initialize agents
    agents = [
        Permabull(),
        ShortSeller(),
        Behavioral(),
        Quant(),
        FirstYear(),
    ]

    # Step 4 — Round 1: Independent views
    print("🎙️  ROUND 1 — Initial positions\n")
    conversation_history = []
    round1_results = []

    for agent in agents:
        print(f"  {agent.name} is speaking...")
        response = agent.speak(briefing, conversation_history=[])
        conversation_history.append({
            "agent": agent.name,
            "response": response
        })
        round1_results.append({
            "agent": agent.name,
            "response": response
        })
        print(f"  ✅ Done.\n")

    # Step 5 — Round 2: Cross examination
    print("⚔️   ROUND 2 — Cross-examination\n")
    round2_results = []

    for agent in agents:
        print(f"  {agent.name} is responding...")
        response = agent.speak(briefing, conversation_history=conversation_history)
        round2_results.append({
            "agent": agent.name,
            "response": response
        })
        print(f"  ✅ Done.\n")

    # Step 6 — Conflict scoring
    print("📊 Computing conflict analysis...")
    conflict = compute_conflict_score(round1_results, round2_results)
    print_conflict_report(conflict)

    # Step 7 — Synthesis
    print("⚖️   SYNTHESIS — Final verdict\n")
    full_history = conversation_history + round2_results
    synthesizer = Synthesizer()
    synthesis = synthesizer.speak(briefing, conversation_history=full_history)
    print("  ✅ Synthesis complete.\n")

    results = {
        "ticker": ticker.upper(),
        "briefing": briefing,
        "round1": round1_results,
        "round2": round2_results,
        "synthesis": synthesis,
        "company_name": data["fundamentals"].get("company_name", ticker),
        "validation": validation,
        "conflict": conflict,
    }

    # Step 8 — Export
    if export:
        filepath = export_debate(results, conflict, validation)
        print(f"💾 Debate exported to: {filepath}\n")
        results["export_path"] = filepath

    return results


def print_arena(results: dict):
    """Pretty print the full debate to terminal."""

    if not results:
        return

    ticker = results["ticker"]
    company = results["company_name"]
    conflict = results["conflict"]
    validation = results["validation"]

    print(f"""
╔══════════════════════════════════════════════════════════════╗
   ARENA — {ticker} ({company})
   Data Quality: {validation['quality_emoji']} {validation['quality']} ({validation['score']}/100)
   Temperature:  {conflict['temperature_emoji']} {conflict['debate_temperature']}
   Polarization: {conflict['polarization_emoji']} {conflict['polarization_label']}
╚══════════════════════════════════════════════════════════════╝""")

    print("\n" + "━"*62)
    print("  ROUND 1 — OPENING POSITIONS")
    print("━"*62)
    for entry in results["round1"]:
        print(f"\n🎙️  {entry['agent'].upper()}")
        print("─" * 50)
        print(entry["response"])

    print("\n" + "━"*62)
    print("  ROUND 2 — CROSS EXAMINATION")
    print("━"*62)
    for entry in results["round2"]:
        print(f"\n⚔️   {entry['agent'].upper()}")
        print("─" * 50)
        print(entry["response"])

    print("\n" + "━"*62)
    print("  FINAL SYNTHESIS")
    print("━"*62)
    print(f"\n⚖️  MODERATOR")
    print("─" * 50)
    print(results["synthesis"])

    print("\n" + "═"*62)
    print("  END OF ARENA SESSION")
    print("═"*62 + "\n")


if __name__ == "__main__":
    ticker = input("Enter ticker (e.g. AAPL, NVDA, RELIANCE.NS): ").strip().upper()
    results = run_arena(ticker)
    if results:
        print_arena(results)