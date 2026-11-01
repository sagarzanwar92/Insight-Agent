
from src.agent.planner import create_plan
from src.agent.sql_agent import generate_sql
from src.agent.analysis_agent import analyze_data
from src.agent.response_agent import generate_response
from src.tools.database_tools import query_database
from src.conversation.manager import ConversationManager


conversation_manager = ConversationManager()

MAX_INVESTIGATION_ROUNDS = 4


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

    # Generate the initial execution plan.
    plan = create_plan(
        question=user_message,
        conversation_history=history
    )

    print("\nEXECUTION PLAN")
    print(plan)

    steps = plan.get("steps", [])

    all_results = []
    all_findings = []
    investigation_log = []

    # --------------------------------------------------
    # STEP 1: DATABASE RETRIEVAL AND ITERATIVE ANALYSIS
    # --------------------------------------------------

    if "query_database" in steps:

        current_question = user_message

        if "analyze_data" in steps:

            for round_number in range(1, MAX_INVESTIGATION_ROUNDS + 1):

                print(
                    f"\nINVESTIGATION ROUND {round_number}"
                )

                # Generate SQL for the current investigation.
                sql = generate_sql(
                    question=current_question,
                    conversation_history=history
                )

                print("\nGENERATED SQL")
                print(sql)

                # Execute the database query.
                results = query_database(sql)

                print("\nQUERY RESULTS")
                print(results)

                all_results.extend(results)

                investigation_log.append({
                    "question": current_question,
                    "sql": sql,
                    "results": results
                })

                # Build context from previous investigations.
                previous_context = (
                    history
                    + "\nInvestigation history:\n"
                    + str(investigation_log)
                )

                # Ask the Analysis Agent to evaluate the evidence.
                analysis = analyze_data(
                    question=user_message,
                    query_results=results,
                    conversation_history=previous_context,
                    previous_findings=all_findings
                )

                print("\nANALYSIS")
                print(analysis)

                # Preserve findings across investigation rounds.
                new_findings = analysis.get("findings", [])
                all_findings.extend(new_findings)

                # Stop when sufficient evidence is available.
                if (
                    analysis.get("assessment") == "sufficient"
                    or not analysis.get("investigation_needed", False)
                ):
                    print("\nSUFFICIENT EVIDENCE FOUND")
                    break

                # Identify the next investigation.
                next_question = analysis.get("next_question")

                if not next_question:
                    print("\nNO FURTHER INVESTIGATION QUESTION")
                    break

                current_question = next_question

            else:
                print(
                    "\nMAXIMUM INVESTIGATION ROUNDS REACHED"
                )

        else:

            # Simple descriptive questions need only one query.
            sql = generate_sql(
                question=user_message,
                conversation_history=history
            )

            print("\nGENERATED SQL")
            print(sql)

            results = query_database(sql)

            print("\nQUERY RESULTS")
            print(results)

            all_results.extend(results)

            investigation_log.append({
                "question": user_message,
                "sql": sql,
                "results": results
            })

    # --------------------------------------------------
    # STEP 2: VISUALIZATION PLACEHOLDER
    # --------------------------------------------------

    if "create_visualization" in steps:

        print("\nVISUALIZATION")
        print(
            "Visualization will be implemented in a later milestone."
        )

    # --------------------------------------------------
    # STEP 3: PREPARE EVIDENCE FOR RESPONSE GENERATION
    # --------------------------------------------------

    response_context = history

    if investigation_log:
        response_context += (
            "\nInvestigation history:\n"
            + str(investigation_log)
        )

    if all_findings:
        response_context += (
            "\nConsolidated findings:\n"
            + str(all_findings)
        )

    # --------------------------------------------------
    # STEP 4: GENERATE FINAL BUSINESS RESPONSE
    # --------------------------------------------------

    answer = generate_response(
        question=user_message,
        results=all_results,
        conversation_history=response_context
    )

    print("\nINSIGHTAGENT ANSWER")
    print(answer)

    # Save the final answer for future follow up questions.
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
