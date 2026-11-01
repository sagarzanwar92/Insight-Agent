
from src.agent.analysis_agent import analyze_data


results = [
    {
        "year": 2018,
        "month": 7,
        "month_name": "July",
        "total_revenue": 1058728.03
    },
    {
        "year": 2018,
        "month": 8,
        "month_name": "August",
        "total_revenue": 1003308.47
    }
]


analysis = analyze_data(
    question="Analyze the revenue change between July and August 2018.",
    query_results=results
)

print("\nANALYSIS RESULTS")
print(analysis)
