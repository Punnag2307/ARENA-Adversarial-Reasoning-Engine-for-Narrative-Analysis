import anthropic
from config import ANTHROPIC_API_KEY, MODEL


def score_agent_stance(client: anthropic.Anthropic, agent_name: str, response: str) -> dict:
    """
    Score an agent's actual stance on THIS specific stock.
    Forces evaluation of argument content, not persona voice.
    """

    prompt = f"""You are scoring the investment stance of an analyst named {agent_name}.

Read their response carefully. Score ONLY based on what they actually say about this specific stock — not their general personality or role.

ANALYST RESPONSE:
{response}

SCORING RULES:
- Score based on the STRENGTH and SPECIFICITY of their bull or bear arguments
- If they make strong specific bear arguments with data: score -0.7 to -1.0
- If they make mild bear arguments: score -0.3 to -0.6
- If they are genuinely uncertain or mixed: score -0.2 to +0.2
- If they make mild bull arguments: score +0.3 to +0.6
- If they make strong specific bull arguments with data: score +0.7 to +1.0
- Do NOT automatically give bears negative scores — read what they actually say
- Do NOT automatically give bulls positive scores — read what they actually say
- A bear who acknowledges some positives should score less negative than pure bear
- Vary your scores — avoid clustering around the same values

Return ONLY valid JSON, no markdown, no explanation:
{{"sentiment_score": <float -1.0 to 1.0>, "stance": "<strongly_bullish|bullish|neutral|bearish|strongly_bearish>", "core_argument": "<one sentence>", "conviction_level": "<high|medium|low>"}}"""

    message = client.messages.create(
        model=MODEL,
        max_tokens=150,
        messages=[{"role": "user", "content": prompt}]
    )

    import json
    try:
        raw = message.content[0].text.strip()
        raw = raw.replace("```json", "").replace("```", "").strip()
        return json.loads(raw)
    except Exception:
        return {
            "sentiment_score": 0.0,
            "stance": "neutral",
            "core_argument": "Could not parse stance",
            "conviction_level": "low"
        }

def compute_conflict_score(round1: list, round2: list) -> dict:
    """
    Analyze the full debate using Claude-based scoring.
    Accurate stance detection regardless of word choice.
    """

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    print("  🧠 Scoring agent stances with Claude...")

    r1_scores = {}
    r2_scores = {}
    r1_details = {}
    r2_details = {}

    # Score Round 1
    for entry in round1:
        agent = entry["agent"]
        print(f"     Scoring {agent} R1...")
        result = score_agent_stance(client, agent, entry["response"])
        r1_scores[agent] = result["sentiment_score"]
        r1_details[agent] = result

    # Score Round 2
    for entry in round2:
        agent = entry["agent"]
        print(f"     Scoring {agent} R2...")
        result = score_agent_stance(client, agent, entry["response"])
        r2_scores[agent] = result["sentiment_score"]
        r2_details[agent] = result

    # Combined average per agent
    all_scores = {}
    for agent in r1_scores:
        r1 = r1_scores.get(agent, 0)
        r2 = r2_scores.get(agent, 0)
        all_scores[agent] = round((r1 + r2) / 2, 3)

    # Drift detection — meaningful threshold
    drift = {}
    for agent in r1_scores:
        if agent in r2_scores:
            r1_val = r1_scores[agent]
            r2_val = r2_scores[agent]
            change = round(r2_val - r1_val, 3)

            # Drift only if change is significant AND direction shifted
            drifted = abs(change) > 0.25

            drift[agent] = {
                "r1": round(r1_val, 3),
                "r2": round(r2_val, 3),
                "drift": round(change, 3),
                "drifted": drifted,
                "r1_stance": r1_details[agent]["stance"],
                "r2_stance": r2_details[agent]["stance"],
                "r1_argument": r1_details[agent]["core_argument"],
                "r2_argument": r2_details[agent]["core_argument"],
            }

    # Polarization index
    scores_list = list(all_scores.values())
    if len(scores_list) > 1:
        polarization = round(max(scores_list) - min(scores_list), 3)
    else:
        polarization = 0.0

    # Dominant voice — most extreme score
    dominant = max(all_scores, key=lambda x: abs(all_scores[x]))

    # Overall debate temperature
    avg_score = round(sum(scores_list) / len(scores_list), 3)
    if avg_score > 0.25:
        temperature = "BULLISH LEAN"
        temp_emoji = "🟢"
    elif avg_score < -0.25:
        temperature = "BEARISH LEAN"
        temp_emoji = "🔴"
    else:
        temperature = "CONTESTED"
        temp_emoji = "⚔️"

    # Polarization label
    if polarization > 0.6:
        polar_label = "HIGHLY POLARIZED"
        polar_emoji = "🔥"
    elif polarization > 0.35:
        polar_label = "MODERATELY POLARIZED"
        polar_emoji = "⚡"
    else:
        polar_label = "MILD DISAGREEMENT"
        polar_emoji = "💬"

    return {
        "agent_scores": all_scores,
        "r1_scores": r1_scores,
        "r2_scores": r2_scores,
        "r1_details": r1_details,
        "r2_details": r2_details,
        "drift": drift,
        "polarization_index": polarization,
        "polarization_label": polar_label,
        "polarization_emoji": polar_emoji,
        "dominant_voice": dominant,
        "debate_temperature": temperature,
        "temperature_emoji": temp_emoji,
        "avg_sentiment": avg_score,
    }


def print_conflict_report(conflict: dict):
    """Print conflict analysis to terminal."""

    print(f"\n{'━'*62}")
    print(f"  CONFLICT ANALYSIS")
    print(f"{'━'*62}")
    print(f"  Temperature:    {conflict['temperature_emoji']} {conflict['debate_temperature']}")
    print(f"  Polarization:   {conflict['polarization_emoji']} {conflict['polarization_label']} (index: {conflict['polarization_index']})")
    print(f"  Dominant Voice: {conflict['dominant_voice']}")

    print(f"\n  AGENT SENTIMENT SCORES (-1.0 bearish → +1.0 bullish)")
    print(f"  {'Agent':<30} {'Score':>6}  {'Stance':<20} Conviction")
    print(f"  {'─'*28} {'─'*6}  {'─'*18} {'─'*10}")

    for agent in conflict["agent_scores"]:
        score = conflict["agent_scores"][agent]
        detail = conflict["r2_details"].get(agent, {})
        stance = detail.get("stance", "N/A")
        conviction = detail.get("conviction_level", "N/A")

        # Visual bar
        bar_len = int(abs(score) * 8)
        bar = "█" * bar_len
        direction = "+" if score >= 0 else "-"

        print(f"  {agent:<30} {direction}{abs(score):.3f}  {stance:<20} {conviction}")

    print(f"\n  DRIFT DETECTION")
    print(f"  {'Agent':<30} {'R1':>6} → {'R2':>6}  Status")
    print(f"  {'─'*28} {'─'*6}   {'─'*6}  {'─'*15}")

    for agent, d in conflict["drift"].items():
        status = "⚠️  DRIFTED" if d["drifted"] else "✅ Stable"
        print(f"  {agent:<30} {d['r1']:>+.3f} → {d['r2']:>+.3f}  {status}")
        if d["drifted"]:
            print(f"  {'':30} R1: {d['r1_stance']} → R2: {d['r2_stance']}")

    print(f"{'━'*62}\n")