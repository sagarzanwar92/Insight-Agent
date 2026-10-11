from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI


PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")

client = OpenAI()


RESPONSE_PROMPT = """
You are InsightAgent, an AI data analyst helping business managers.

Answer the user's latest business question using the supplied query
results and conversation history.

Rules:
1. Base factual claims only on the supplied results and context.
2. Do not invent figures or explanations.
3. If the results are insufficient, clearly state what is missing.
4. Explain findings in concise, business friendly language.
5. Include relevant numbers and units where available.
6. Do not include SQL unless the user asks for it.
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
Conversation history:
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