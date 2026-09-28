from pathlib import Path
import pandas as pd


CLEANED_DIR = Path("data/processed/cleaned")
CURATED_DIR = Path("data/curated")

CURATED_DIR.mkdir(parents=True, exist_ok=True)


def create_fact_orders():

    orders = pd.read_csv(CLEANED_DIR / "orders.csv")
    customers = pd.read_csv(CLEANED_DIR / "customers.csv")

    fact_orders = orders.merge(
        customers[
            [
                "customer_id",
                "customer_unique_id",
                "customer_zip_code_prefix",
            ]
        ],
        on="customer_id",
        how="left",
        validate="one_to_one",
    )

    date_columns = [
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ]

    for column in date_columns:
        fact_orders[column] = pd.to_datetime(
            fact_orders[column],
            errors="coerce",
        )

    output_file = CURATED_DIR / "fact_orders.csv"

    fact_orders.to_csv(
        output_file,
        index=False,
    )

    print(f"Created: {output_file}")
    print(f"Rows: {len(fact_orders):,}")
    print(f"Columns: {len(fact_orders.columns)}")


def create_fact_order_items():

    order_items = pd.read_csv(
        CLEANED_DIR / "order_items.csv"
    )

    products = pd.read_csv(
        CLEANED_DIR / "products.csv"
    )

    sellers = pd.read_csv(
        CLEANED_DIR / "sellers.csv"
    )

    fact_order_items = order_items.merge(
        products[
            [
                "product_id",
                "product_category_name",
                "product_weight_g",
                "product_length_cm",
                "product_height_cm",
                "product_width_cm",
            ]
        ],
        on="product_id",
        how="left",
        validate="many_to_one",
    )

    fact_order_items = fact_order_items.merge(
        sellers[
            [
                "seller_id",
                "seller_zip_code_prefix",
            ]
        ],
        on="seller_id",
        how="left",
        validate="many_to_one",
    )

    fact_order_items["item_revenue"] = (
        fact_order_items["price"]
        + fact_order_items["freight_value"]
    )

    output_file = CURATED_DIR / "fact_order_items.csv"

    fact_order_items.to_csv(
        output_file,
        index=False,
    )

    print(f"Created: {output_file}")
    print(f"Rows: {len(fact_order_items):,}")
    print(f"Columns: {len(fact_order_items.columns)}")

def create_fact_payments():

    payments = pd.read_csv(
        CLEANED_DIR / "order_payments.csv"
    )

    payments["payment_type"] = payments["payment_type"].fillna("unknown")

    payments["payment_value"] = pd.to_numeric(
        payments["payment_value"],
        errors="coerce",
    )

    payments["payment_installments"] = pd.to_numeric(
        payments["payment_installments"],
        errors="coerce",
    )

    output_file = CURATED_DIR / "fact_payments.csv"

    payments.to_csv(
        output_file,
        index=False,
    )

    print(f"Created: {output_file}")
    print(f"Rows: {len(payments):,}")
    print(f"Columns: {len(payments.columns)}")

def create_dim_products():

    products = pd.read_csv(
        CLEANED_DIR / "products.csv"
    )

    output_file = CURATED_DIR / "dim_products.csv"

    products.to_csv(
        output_file,
        index=False,
    )

    print(f"Created: {output_file}")
    print(f"Rows: {len(products):,}")
    print(f"Columns: {len(products.columns)}")

def create_dim_customers():

    customers = pd.read_csv(
        CLEANED_DIR / "customers.csv"
    )

    output_file = CURATED_DIR / "dim_customers.csv"

    customers.to_csv(
        output_file,
        index=False,
    )

    print(f"Created: {output_file}")
    print(f"Rows: {len(customers):,}")
    print(f"Columns: {len(customers.columns)}")


def create_dim_sellers():

    sellers = pd.read_csv(
        CLEANED_DIR / "sellers.csv"
    )

    output_file = CURATED_DIR / "dim_sellers.csv"

    sellers.to_csv(
        output_file,
        index=False,
    )

    print(f"Created: {output_file}")
    print(f"Rows: {len(sellers):,}")
    print(f"Columns: {len(sellers.columns)}")

def create_dim_date():

    orders = pd.read_csv(
        CLEANED_DIR / "orders.csv"
    )

    orders["order_purchase_timestamp"] = pd.to_datetime(
        orders["order_purchase_timestamp"],
        errors="coerce",
    )

    start_date = orders["order_purchase_timestamp"].min().normalize()
    end_date = orders["order_purchase_timestamp"].max().normalize()

    dates = pd.date_range(
        start=start_date,
        end=end_date,
        freq="D",
    )

    dim_date = pd.DataFrame({
        "date": dates,
    })

    dim_date["year"] = dim_date["date"].dt.year
    dim_date["quarter"] = dim_date["date"].dt.quarter
    dim_date["month"] = dim_date["date"].dt.month
    dim_date["month_name"] = dim_date["date"].dt.month_name()
    dim_date["week"] = dim_date["date"].dt.isocalendar().week.astype(int)
    dim_date["day"] = dim_date["date"].dt.day
    dim_date["day_name"] = dim_date["date"].dt.day_name()
    dim_date["is_weekend"] = dim_date["date"].dt.dayofweek >= 5

    output_file = CURATED_DIR / "dim_date.csv"

    dim_date.to_csv(
        output_file,
        index=False,
    )

    print(f"Created: {output_file}")
    print(f"Rows: {len(dim_date):,}")
    print(f"Columns: {len(dim_date.columns)}")

def validate_curated_data():

    checks = []

    fact_orders = pd.read_csv(
        CURATED_DIR / "fact_orders.csv"
    )

    fact_order_items = pd.read_csv(
        CURATED_DIR / "fact_order_items.csv"
    )

    fact_payments = pd.read_csv(
        CURATED_DIR / "fact_payments.csv"
    )

    dim_products = pd.read_csv(
        CURATED_DIR / "dim_products.csv"
    )

    dim_customers = pd.read_csv(
        CURATED_DIR / "dim_customers.csv"
    )

    dim_sellers = pd.read_csv(
        CURATED_DIR / "dim_sellers.csv"
    )

    # Orders must have unique order IDs
    checks.append({
        "check": "fact_orders.order_id unique",
        "status": (
            "PASS"
            if fact_orders["order_id"].is_unique
            else "FAIL"
        ),
    })

    # Customers must have unique customer IDs
    checks.append({
        "check": "dim_customers.customer_id unique",
        "status": (
            "PASS"
            if dim_customers["customer_id"].is_unique
            else "FAIL"
        ),
    })

    # Products must have unique product IDs
    checks.append({
        "check": "dim_products.product_id unique",
        "status": (
            "PASS"
            if dim_products["product_id"].is_unique
            else "FAIL"
        ),
    })

    # Sellers must have unique seller IDs
    checks.append({
        "check": "dim_sellers.seller_id unique",
        "status": (
            "PASS"
            if dim_sellers["seller_id"].is_unique
            else "FAIL"
        ),
    })

    # Order items must reference existing products
    invalid_products = (
        ~fact_order_items["product_id"]
        .isin(dim_products["product_id"])
    ).sum()

    checks.append({
        "check": "order_items → products",
        "status": (
            "PASS"
            if invalid_products == 0
            else "FAIL"
        ),
        "details": f"Invalid references={invalid_products}",
    })

    # Order items must reference existing sellers
    invalid_sellers = (
        ~fact_order_items["seller_id"]
        .isin(dim_sellers["seller_id"])
    ).sum()

    checks.append({
        "check": "order_items → sellers",
        "status": (
            "PASS"
            if invalid_sellers == 0
            else "FAIL"
        ),
        "details": f"Invalid references={invalid_sellers}",
    })

    # Payments must reference existing orders
    invalid_payment_orders = (
        ~fact_payments["order_id"]
        .isin(fact_orders["order_id"])
    ).sum()

    checks.append({
        "check": "payments → orders",
        "status": (
            "PASS"
            if invalid_payment_orders == 0
            else "FAIL"
        ),
        "details": f"Invalid references={invalid_payment_orders}",
    })

    # Revenue calculation must remain correct
    revenue_check = (
    (
        fact_order_items["item_revenue"]
        - (
            fact_order_items["price"]
            + fact_order_items["freight_value"]
        )
    ).abs()
    < 0.000001).all()

    checks.append({
        "check": "item_revenue calculation",
        "status": (
            "PASS"
            if revenue_check
            else "FAIL"
        ),
    })

    # Required keys should not be null
    required_columns = {
        "fact_orders": fact_orders,
        "fact_order_items": fact_order_items,
        "fact_payments": fact_payments,
        "dim_products": dim_products,
        "dim_customers": dim_customers,
        "dim_sellers": dim_sellers,
    }

    for table_name, df in required_columns.items():

        null_count = int(df.isna().sum().sum())

        checks.append({
            "check": f"{table_name} null check",
            "status": (
                "PASS"
                if null_count == 0
                else "WARNING"
            ),
            "details": f"Null values={null_count}",
        })

    print("\n" + "=" * 60)
    print("CURATED DATA VALIDATION")
    print("=" * 60)

    for check in checks:

        details = check.get("details", "")

        print(
            f"{check['status']:8} "
            f"{check['check']:35} "
            f"{details}"
        )

    failures = sum(
        check["status"] == "FAIL"
        for check in checks
    )

    warnings = sum(
        check["status"] == "WARNING"
        for check in checks
    )

    print("\n" + "=" * 60)
    print(f"Failures: {failures}")
    print(f"Warnings: {warnings}")
    print("=" * 60)

if __name__ == "__main__":

    create_fact_orders()
    create_fact_order_items()
    create_fact_payments()
    create_dim_products()
    create_dim_customers()
    create_dim_sellers()
    create_dim_date()

    validate_curated_data()