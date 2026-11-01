
from src.agent.planner import create_plan


questions = [
    "How many orders are in the database?",
    "Why did revenue decline in August 2018?",
    "Which product categories contributed to the decline?",
    "What did I ask about previously?"
]


history = """
user: What was the revenue change between July and August 2018?
assistant: Revenue declined by approximately 5.23%.
"""


for question in questions:

    print("\nQUESTION:", question)

    plan = create_plan(
        question=question,
        conversation_history=history
    )

    print("PLAN:", plan)
