import anthropic
from config import ANTHROPIC_API_KEY, MODEL, MAX_TOKENS


class BaseAgent:
    def __init__(self, name: str, system_prompt: str):
        self.name = name
        self.system_prompt = system_prompt
        self.client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    def speak(self, briefing: str, conversation_history: list = None) -> str:
        """
        Generate this agent's analysis.
        conversation_history: list of previous agent outputs to respond to.
        """

        # Hallucination guard — injected into every prompt
        hallucination_guard = """
CRITICAL RULES — NON-NEGOTIABLE:
1. You may ONLY cite numbers, statistics, or data points that appear 
   explicitly in the briefing below.
2. If a data field shows N/A, you must acknowledge the absence — 
   never invent or estimate a substitute figure.
3. You may use your domain knowledge for interpretation and reasoning,
   but every factual claim must trace back to the briefing.
4. If you violate these rules, your analysis is worthless.
"""

        if conversation_history:
            prior_debate = "\n\n".join([
                f"{entry['agent']} said:\n{entry['response']}"
                for entry in conversation_history
            ])

            # Drift prevention — remind agent of their non-negotiables
            drift_guard = f"""
PERSONA LOCK — You are {self.name}. Your core worldview does NOT change 
under pressure. You may acknowledge strong points but you never abandon 
your fundamental framework. If others make good arguments, engage — 
but do not capitulate. Stay in character completely.
"""

            user_message = f"""
{hallucination_guard}

{drift_guard}

Here is the financial briefing — your ONLY source of facts:

{briefing}

---

Here is what other analysts have said so far:

{prior_debate}

---

Now respond. You MUST:
- Directly challenge at least one specific claim made above by name
- Cite at least two numbers from the briefing to support your position
- Stay completely in character — your worldview does not bend
"""
        else:
            user_message = f"""
{hallucination_guard}

Here is the financial briefing — your ONLY source of facts:

{briefing}

---

Give your initial analysis. You MUST:
- Reference at least three specific numbers from the briefing
- Stay completely in character
- Be direct and take a clear position
"""

        message = self.client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            system=self.system_prompt,
            messages=[{"role": "user", "content": user_message}]
        )

        return message.content[0].text