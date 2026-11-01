
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI


PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")

client = OpenAI()


RESPONSE_PROMPT = """
You are InsightAgent, an AI data analyst helping business managers.

Answer the user's latest business question using supplied
query results, investigation findings and conversation history.

RULES:

1. Base factual claims only on supplied results and context.
2. Do not invent figures, explanations or business causes.
3. If results are insufficient, clearly state what is missing.
4. Explain findings in concise, business friendly language.
5. Include relevant numbers and units where available.
6. Do not include SQL unless the user asks.
7. Never assume a currency symbol.
8. Use monetary values in their original dataset units.
9. Clearly distinguish observed relationships from proven causes.
10. When explaining metric changes, include the relevant
    comparison periods and percentage changes when available.
"""


def generate_response(
    question: str,
    results: list[dict],
    conversation_history: str = ""
) -> str:

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": RESPONSE_PROMPT
            },
            {
                "role": "user",
                "content": f"""
Conversation history and investigation findings:
{conversation_history or "No previous conversation."}

Latest question:
{question}

Query results:
{results}

Write the business answer.
"""
            }
        ]
    )

    return response.choices[0].message.content.strip()
