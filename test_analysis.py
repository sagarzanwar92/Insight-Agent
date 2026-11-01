
from src.agent.analysis_agent import analyze_data


results = [
    {
        "month": "July",
        "revenue": 1058728.03
    },
    {
        "month": "August",
        "revenue": 1003308.47
    }
]


result = analyze_data(
    question="Why did revenue decline between July and August 2018?",
    query_results=results
)


print("\nSTRUCTURED ANALYSIS")
print(result)

print("\nASSESSMENT:", result["assessment"])
print("INVESTIGATION NEEDED:", result["investigation_needed"])
print("NEXT QUESTION:", result["next_question"])
