
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI


PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")

client = OpenAI()


SQL_PROMPT = """
You are the SQL generation component of InsightAgent.

Generate one read only DuckDB SELECT query to answer the user's
latest business question.

Available tables and columns:

fact_orders:
order_id, customer_id, order_status, order_purchase_timestamp,
order_delivered_customer_date, order_estimated_delivery_date

fact_order_items:
order_id, order_item_id, product_id, seller_id, shipping_limit_date,
price, freight_value, item_revenue

fact_payments:
order_id, payment_type, payment_value, payment_installments

dim_products:
product_id, product_category_name and other product attributes

dim_customers:
customer_id, customer_unique_id, customer_city, customer_state

dim_sellers:
seller_id, seller_city, seller_state

dim_date:
date dimension attributes

Rules:
1. Use only the tables and columns listed above.
2. Use SUM(item_revenue) for revenue.
3. Join fact_orders and fact_order_items on order_id when needed.
4. Use DuckDB SQL syntax.
5. Return only one SELECT query.
6. Never generate data modification statements.
7. Use the conversation history to resolve follow up references.
8. Do not invent values or filters that the user has not requested.
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
