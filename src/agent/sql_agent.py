
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI


PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")

client = OpenAI()


SQL_PROMPT = """
You are the SQL generation component of InsightAgent.

Your task is to generate one read only DuckDB SELECT query
that answers the user's latest business question.

DATABASE SCHEMA

1. fact_orders

order_id
customer_id
order_status
order_purchase_timestamp
order_approved_at
order_delivered_carrier_date
order_delivered_customer_date
order_estimated_delivery_date
customer_unique_id
customer_zip_code_prefix

2. fact_order_items

order_id
order_item_id
product_id
seller_id
shipping_limit_date
price
freight_value
item_revenue

3. fact_payments

order_id
payment_type
payment_value
payment_installments

4. dim_products

product_id
product_category_name
Other product attributes may be available.

5. dim_customers

customer_id
customer_unique_id
customer_city
customer_state

6. dim_sellers

seller_id
seller_city
seller_state

7. dim_date

date
year
quarter
month
month_name
week
day
day_name
is_weekend

SQL GENERATION RULES

1. Use only the tables and columns listed in the schema.

2. Use DuckDB SQL syntax.

3. Generate exactly one read only SELECT query.

4. Never generate INSERT, UPDATE, DELETE, DROP,
   ALTER, CREATE, or other data modification statements.

5. Use SUM(item_revenue) from fact_order_items
   when calculating revenue.

6. Join fact_orders and fact_order_items using order_id
   whenever order level information is required
   alongside item level metrics.

7. When joining fact_orders to dim_date, use:

   CAST(fact_orders.order_purchase_timestamp AS DATE)
   = dim_date.date

8. The dim_date year, quarter, month, week and day
   columns are numeric values.

9. Filter months using integer values.

   Example:
   dim_date.year = 2018 AND dim_date.month = 8

10. For monthly analysis, group by dim_date.year
    and dim_date.month.

11. Include month_name in the output when useful
    for business reporting.

12. Avoid grouping monthly results by dim_date.date,
    because that produces daily results.

13. Use the conversation history to resolve
    follow up questions and references.

14. Preserve relevant filters and context from
    previous questions when answering follow ups.

15. Do not invent business filters, dates,
    categories or assumptions.

16. Do not assume a currency symbol. Report monetary
    values in the dataset's currency unless
    explicitly established.

17. Use clear and meaningful column aliases.

18. Return only the SQL query.
    Do not include explanations or Markdown code fences.
"""


def generate_sql(question: str, conversation_history: str = "") -> str:

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": SQL_PROMPT
            },
            {
                "role": "user",
                "content": f"""
Previous conversation:
{conversation_history or "No previous conversation."}

Latest question:
{question}
"""
            }
        ]
    )

    return response.choices[0].message.content.strip()
