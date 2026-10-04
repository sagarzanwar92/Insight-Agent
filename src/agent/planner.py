from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI


PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")

client = OpenAI()


PLANNER_PROMPT = """
You are the planning component of an AI Data Analyst.

Your job is to understand a user's business question and determine
what actions are required to answer it.

Available actions:

query_database
Use when factual information must be retrieved from the database.

analyze_data
Use when retrieved data needs comparison, calculation, trend analysis,
decomposition, or explanation.

create_visualization
Use when the user explicitly asks for a chart or when visualization
would materially improve understanding.

Return ONLY valid JSON using this structure:

{
    "question_type": "descriptive | diagnostic | analytical",
    "requires_database": true,
    "requires_analysis": true,
    "requires_visualization": true,
    "steps": [
        "query_database",
        "analyze_data",
        "create_visualization"
    ]
}

Do not answer the user's business question.
Do not include any additional text.
"""

def create_plan(question: str):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": PLANNER_PROMPT
            },
            {
                "role": "user",
                "content": question
            }
        ],
        response_format={
            "type": "json_object"
        }
    )

    return response.choices[0].message.content