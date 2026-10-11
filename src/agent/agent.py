from src.agent.planner import create_plan
from src.agent.sql_agent import generate_sql
from src.tools.database_tools import query_database
from src.conversation.manager import ConversationManager

from src.agent.response_agent import generate_response

conversation_manager = ConversationManager()


def run_agent(conversation_id: str, user_message: str):
    state = conversation_manager.get_or_create(conversation_id)

    # Capture conversation history before adding the latest question.
    history = "\n".join(
        f"{message['role']}: {message['content']}"
        for message in state.messages
    )

    state.messages.append({
        "role": "user",
        "content": user_message
    })

    # Route questions about conversation history without SQL.
    memory_question = any(
        phrase in user_message.lower()
        for phrase in [
            "what did i ask",
            "which metric did i ask",
            "what did i mention",
            "what did we discuss",
            "what was your previous answer"
        ]
    )

    if memory_question:
        answer = generate_response(
            question=user_message,
            results=[],
            conversation_history=history
        )

        print("\nINSIGHTAGENT ANSWER")
        print(answer)

        state.messages.append({
            "role": "assistant",
            "content": answer
        })

        conversation_manager.save(state)
        return answer

    # Prepare input for the planner.
    planning_input = f"""
Previous conversation:
{history or "No previous messages."}

Latest user question:
{user_message}
"""

    # Generate the execution plan.
    plan = create_plan(planning_input)

    print("\nEXECUTION PLAN")
    print(plan)

    # Generate SQL.
    sql = generate_sql(
        question=user_message,
        conversation_history=history
    )

    print("\nGENERATED SQL")
    print(sql)

    # Execute SQL against DuckDB.
    results = query_database(sql)

    print("\nQUERY RESULTS")
    print(results)

    # Generate a business friendly answer.
    answer = generate_response(
        question=user_message,
        results=results,
        conversation_history=history
    )

    print("\nINSIGHTAGENT ANSWER")
    print(answer)

    # Store the answer for future follow up questions.
    state.messages.append({
        "role": "assistant",
        "content": answer
    })

    conversation_manager.save(state)

    return answer


if __name__ == "__main__":
    conversation_id = "local-test-session"

    while True:
        question = input(
            "\nAsk a business question (or type 'exit'): "
        )

        if question.strip().lower() == "exit":
            break

        if not question.strip():
            continue

        try:
            run_agent(conversation_id, question)
        except Exception as error:
            print(f"\nAgent error: {error}")
