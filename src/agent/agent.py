from src.agent.planner import create_plan
from src.agent.sql_agent import generate_sql
from src.agent.response_agent import generate_response
from src.tools.database_tools import query_database
from src.conversation.manager import ConversationManager

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

    # Generate execution plan using the latest question and history.
    plan = create_plan(
        question=user_message,
        conversation_history=history
    )

    print("\nEXECUTION PLAN")
    print(plan)

    steps = plan.get("steps", [])
    results = []

    # Execute actions according to the planner's decisions.

    if "query_database" in steps:

        sql = generate_sql(
            question=user_message,
            conversation_history=history
        )

        print("\nGENERATED SQL")
        print(sql)

        results = query_database(sql)

        print("\nQUERY RESULTS")
        print(results)

    if "analyze_data" in steps:
        print("\nANALYSIS")
        print("Analysis has been requested by the planner.")
        # Analysis tool will be connected in the next milestone.

    if "create_visualization" in steps:
        print("\nVISUALIZATION")
        print("Visualization has been requested by the planner.")
        # Visualization tool will be connected in a later milestone.

    # Generate the final business response.
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