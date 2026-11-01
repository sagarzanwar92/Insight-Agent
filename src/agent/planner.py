
from pathlib import Path
import json

from dotenv import load_dotenv
from openai import OpenAI


PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")

client = OpenAI()


PLANNER_PROMPT = """
You are the planning component of InsightAgent, an AI Data Analyst.

Understand the user's latest question, consider the conversation
history, and determine the actions required.

AVAILABLE ACTIONS:

1. query_database
Retrieve factual information from the database.

2. analyze_data
Interpret retrieved evidence, identify patterns, evaluate
hypotheses and determine whether further investigation is needed.

3. create_visualization
Create a chart when explicitly requested or materially useful.

4. answer_from_memory
Answer questions about previous questions, answers or findings
using conversation history without querying the database.

DECISION RULES:

1. Use answer_from_memory when the question can be answered
   entirely from conversation history.

2. Use query_database when fresh factual information is required.

3. Use analyze_data when interpretation, comparisons, trends,
   diagnostic reasoning or recommendations are required.

4. Use create_visualization when a chart is requested or useful.

5. Diagnostic questions generally require both query_database
   and analyze_data.

6. Analytical questions generally require both query_database
   and analyze_data.

7. Simple descriptive questions may require only query_database.

8. Follow up questions must inherit relevant context from
   previous conversation messages.

9. A follow up question may introduce a new dimension,
   geography, category or metric while retaining relevant
   context from the earlier discussion.

10. Do not add unnecessary actions.

IMPORTANT:
The Analysis Agent will independently decide whether additional
investigation is required after reviewing database evidence.
Do not attempt to predict all investigation queries in advance.

RETURN ONLY VALID JSON:

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


def create_plan(
    question: str,
    conversation_history: str = ""
) -> dict:

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

    return json.loads(
        response.choices[0].message.content
    )
