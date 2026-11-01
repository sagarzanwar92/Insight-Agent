from pathlib import Path
import json

from dotenv import load_dotenv
from openai import OpenAI


PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")

client = OpenAI()


PLANNER_PROMPT = """
You are the planning component of InsightAgent, an AI Data Analyst.

Your job is to understand the latest user question, consider the
conversation history, and determine which actions are required.

Available actions:

1. query_database
Retrieve factual information from the database.

2. analyze_data
Perform calculations, comparisons, trend analysis, decomposition,
or interpret retrieved data.

3. create_visualization
Create a chart when explicitly requested or materially useful.

4. answer_from_memory
Answer questions about previous questions, answers, or findings
using conversation history without querying the database.

Decision rules:

1. Use answer_from_memory when the question can be answered
   entirely from conversation history.

2. Use query_database when fresh factual data is required.

3. Use analyze_data when calculations, comparisons, trends,
   or diagnostic explanations are required.

4. Use create_visualization when a chart is requested or useful.

5. A follow up question must inherit relevant context from
   previous conversation messages.

6. Do not add unnecessary actions.

Return ONLY valid JSON using this structure:

{
    "question_type": "descriptive",
    "requires_database": true,
    "requires_analysis": false,
    "requires_visualization": false,
    "steps": ["query_database"]
}

Allowed question_type values:
descriptive, diagnostic, analytical, conversational

Allowed steps:
answer_from_memory, query_database, analyze_data,
create_visualization

Do not answer the business question.
Do not include additional text.
"""


def create_plan(question: str, conversation_history: str = "") -> dict:

    planning_input = f"""
        Previous conversation:
        {conversation_history or "No previous conversation."}

        Latest user question:
        {question}
        """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": PLANNER_PROMPT
            },
            {
                "role": "user",
                "content": planning_input
            }
        ],
        response_format={
            "type": "json_object"
        }
    )

    plan = json.loads(response.choices[0].message.content)

    return plan