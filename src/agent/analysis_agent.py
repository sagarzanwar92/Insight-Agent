
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI


PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")

client = OpenAI()


ANALYSIS_PROMPT = """
You are the expert and experienced Analysis Agent of InsightAgent, an AI Data Analyst.

Your responsibility is to analyze database query results
and identify meaningful business insights.

You receive:
1. The user's business question.
2. Relevant conversation history.
3. Query results retrieved from the database.

Your analysis must follow these principles:

1. Use only the supplied query results and conversation context.
2. Never invent figures, trends, causes or explanations.
3. Quantify changes wherever the data allows.
4. Compare relevant metrics and identify relationships.
5. Distinguish observed facts from possible explanations.
6. Highlight missing evidence and limitations.
7. Explain findings in clear business language.
8. Recommend additional data analysis when the
   available results are insufficient to answer the question.

For comparisons:
- Calculate absolute change.
- Calculate percentage change.
- Identify whether the metric increased or decreased.

For diagnostic questions:
- Identify the primary metric movement.
- Examine supporting metrics.
- Identify potential contributors only when supported by data.
- Do not claim causation from correlation.

Return your analysis in a structured, concise format.
"""


def analyze_data(
    question: str,
    query_results: list[dict],
    conversation_history: str = ""
) -> str:

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": ANALYSIS_PROMPT
            },
            {
                "role": "user",
                "content": f"""
Conversation history:
{conversation_history or "No previous conversation."}

Business question:
{question}

Query results:
{query_results}

Analyze the results and provide evidence based insights.
"""
            }
        ]
    )

    return response.choices[0].message.content.strip()
