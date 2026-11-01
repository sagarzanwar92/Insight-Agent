
import math
from statistics import mean
from typing import Any, Iterable


# --------------------------------------------------
# 1. COMMON VALIDATION AND RESULT HELPERS
# --------------------------------------------------

def _validate_number(value: Any, name: str) -> float:

    if isinstance(value, bool):
        raise ValueError(f"{name} must be numeric.")

    try:
        number = float(value)
    except (TypeError, ValueError):
        raise ValueError(f"{name} must be numeric.")

    if not math.isfinite(number):
        raise ValueError(f"{name} must be finite.")

    return number


def _make_result(
    analysis_type: str,
    metric: str,
    results: dict,
    warnings: list | None = None
) -> dict:

    return {
        "analysis_type": analysis_type,
        "metric": metric,
        "status": "success",
        "results": results,
        "warnings": warnings or []
    }


def _make_error(
    analysis_type: str,
    metric: str,
    error: Exception
) -> dict:

    return {
        "analysis_type": analysis_type,
        "metric": metric,
        "status": "error",
        "results": {},
        "warnings": [str(error)]
    }


# --------------------------------------------------
# 2. CHANGE AND GROWTH CALCULATIONS
# --------------------------------------------------

def calculate_change(
    previous_value: float,
    current_value: float,
    metric: str = "metric"
) -> dict:

    try:
        previous = _validate_number(
            previous_value, "previous_value"
        )

        current = _validate_number(
            current_value, "current_value"
        )

        absolute_change = current - previous

        percentage_change = (
            (absolute_change / abs(previous)) * 100
            if previous != 0
            else None
        )

        if absolute_change > 0:
            direction = "increase"
        elif absolute_change < 0:
            direction = "decrease"
        else:
            direction = "no_change"

        warnings = []

        if percentage_change is None:
            warnings.append(
                "Percentage change is undefined because "
                "the previous value is zero."
            )

        return _make_result(
            "change",
            metric,
            {
                "previous_value": previous,
                "current_value": current,
                "absolute_change": round(absolute_change, 4),
                "percentage_change": (
                    round(percentage_change, 4)
                    if percentage_change is not None
                    else None
                ),
                "direction": direction
            },
            warnings
        )

    except Exception as error:
        return _make_error("change", metric, error)


def calculate_growth_rate(
    previous_value: float,
    current_value: float,
    metric: str = "metric"
) -> dict:

    result = calculate_change(
        previous_value,
        current_value,
        metric
    )

    result["analysis_type"] = "growth_rate"

    return result


# --------------------------------------------------
# 3. AVERAGE AND RATIO
# --------------------------------------------------

def calculate_average(
    values: Iterable[float] | float,
    count: int | None = None,
    metric: str = "metric"
) -> dict:

    try:
        if count is not None:

            total = _validate_number(values, "total_value")

            if isinstance(count, bool) or not isinstance(count, int):
                raise ValueError("count must be an integer.")

            if count < 0:
                raise ValueError("count cannot be negative.")

            if count == 0:
                return _make_result(
                    "average",
                    metric,
                    {"average": None, "count": 0},
                    ["Average is undefined because count is zero."]
                )

            average_value = total / count
            number_of_values = count

        else:

            if isinstance(values, (int, float)):
                raise ValueError(
                    "Provide count when passing a total value."
                )

            numeric_values = [
                _validate_number(value, "value")
                for value in values
            ]

            if not numeric_values:
                return _make_result(
                    "average",
                    metric,
                    {"average": None, "count": 0},
                    ["Cannot calculate an average from an empty collection."]
                )

            average_value = mean(numeric_values)
            number_of_values = len(numeric_values)

        return _make_result(
            "average",
            metric,
            {
                "average": round(average_value, 4),
                "count": number_of_values
            }
        )

    except Exception as error:
        return _make_error("average", metric, error)


def calculate_ratio(
    numerator: float,
    denominator: float,
    metric: str = "ratio"
) -> dict:

    try:
        numerator = _validate_number(numerator, "numerator")
        denominator = _validate_number(denominator, "denominator")

        if denominator == 0:
            return _make_result(
                "ratio",
                metric,
                {
                    "numerator": numerator,
                    "denominator": denominator,
                    "ratio": None,
                    "percentage": None
                },
                ["Ratio is undefined because denominator is zero."]
            )

        ratio = numerator / denominator

        return _make_result(
            "ratio",
            metric,
            {
                "numerator": numerator,
                "denominator": denominator,
                "ratio": round(ratio, 4),
                "percentage": round(ratio * 100, 4)
            }
        )

    except Exception as error:
        return _make_error("ratio", metric, error)


# --------------------------------------------------
# 4. CONTRIBUTION ANALYSIS
# --------------------------------------------------

def calculate_contribution(
    component_change: float,
    total_change: float,
    component: str = "component"
) -> dict:

    try:
        component_value = _validate_number(
            component_change, "component_change"
        )

        total_value = _validate_number(
            total_change, "total_change"
        )

        if total_value == 0:
            return _make_result(
                "contribution",
                component,
                {
                    "component_change": component_value,
                    "total_change": total_value,
                    "contribution_percentage": None
                },
                ["Contribution is undefined because total change is zero."]
            )

        contribution = (
            component_value / total_value
        ) * 100

        return _make_result(
            "contribution",
            component,
            {
                "component_change": component_value,
                "total_change": total_value,
                "contribution_percentage": round(contribution, 4)
            }
        )

    except Exception as error:
        return _make_error("contribution", component, error)


# --------------------------------------------------
# 5. DISTRIBUTION AND RANKING
# --------------------------------------------------

def calculate_distribution(
    records: list[dict],
    dimension: str,
    value: str,
    top_n: int | None = None
) -> dict:

    try:
        if not records:
            return _make_result(
                "distribution",
                value,
                {"categories": [], "total": 0},
                ["No records supplied."]
            )

        totals = {}

        for record in records:

            if dimension not in record or value not in record:
                raise ValueError(
                    f"Missing required column: {dimension} or {value}."
                )

            category = record[dimension]
            amount = _validate_number(record[value], value)

            totals[category] = totals.get(category, 0) + amount

        overall_total = sum(totals.values())

        categories = []

        for category, amount in totals.items():

            share = (
                (amount / overall_total) * 100
                if overall_total != 0
                else None
            )

            categories.append({
                "category": category,
                "value": round(amount, 4),
                "share_percentage": (
                    round(share, 4)
                    if share is not None
                    else None
                )
            })

        categories.sort(
            key=lambda item: item["value"],
            reverse=True
        )

        if top_n is not None:

            if (
                isinstance(top_n, bool)
                or not isinstance(top_n, int)
                or top_n < 1
            ):
                raise ValueError("top_n must be a positive integer.")

            categories = categories[:top_n]

        return _make_result(
            "distribution",
            value,
            {
                "dimension": dimension,
                "total": round(overall_total, 4),
                "categories": categories
            }
        )

    except Exception as error:
        return _make_error("distribution", value, error)


def rank_categories(
    records: list[dict],
    dimension: str,
    value: str,
    ascending: bool = False,
    top_n: int | None = None
) -> dict:

    try:
        result = calculate_distribution(
            records=records,
            dimension=dimension,
            value=value
        )

        if result["status"] == "error":
            return result

        categories = result["results"]["categories"]

        categories.sort(
            key=lambda item: item["value"],
            reverse=not ascending
        )

        if top_n is not None:

            if (
                isinstance(top_n, bool)
                or not isinstance(top_n, int)
                or top_n < 1
            ):
                raise ValueError("top_n must be a positive integer.")

            categories = categories[:top_n]

        for rank, category in enumerate(categories, start=1):
            category["rank"] = rank

        result["analysis_type"] = "ranking"
        result["results"]["categories"] = categories

        return result

    except Exception as error:
        return _make_error("ranking", value, error)


# --------------------------------------------------
# 6. CORRELATION
# --------------------------------------------------

def calculate_correlation(
    records: list[dict],
    x: str,
    y: str
) -> dict:

    metric = f"{x} and {y}"

    try:
        if not records:
            return _make_result(
                "correlation",
                metric,
                {"correlation": None},
                ["No records supplied."]
            )

        x_values = []
        y_values = []

        for record in records:

            if x not in record or y not in record:
                raise ValueError(
                    f"Missing required columns: {x} or {y}."
                )

            x_values.append(_validate_number(record[x], x))
            y_values.append(_validate_number(record[y], y))

        if len(x_values) < 2:
            return _make_result(
                "correlation",
                metric,
                {"correlation": None},
                ["At least two observations are required."]
            )

        x_mean = mean(x_values)
        y_mean = mean(y_values)

        covariance = sum(
            (a - x_mean) * (b - y_mean)
            for a, b in zip(x_values, y_values)
        )

        x_variance = sum(
            (a - x_mean) ** 2 for a in x_values
        )

        y_variance = sum(
            (b - y_mean) ** 2 for b in y_values
        )

        if x_variance == 0 or y_variance == 0:
            return _make_result(
                "correlation",
                metric,
                {"correlation": None},
                ["Correlation is undefined for a constant variable."]
            )

        correlation = covariance / math.sqrt(
            x_variance * y_variance
        )

        return _make_result(
            "correlation",
            metric,
            {"correlation": round(correlation, 4)}
        )

    except Exception as error:
        return _make_error("correlation", metric, error)


# --------------------------------------------------
# 7. OUTLIER DETECTION
# --------------------------------------------------

def detect_outliers(
    values: Iterable[float],
    method: str = "iqr",
    threshold: float = 1.5
) -> dict:

    try:
        if method.lower() != "iqr":
            raise ValueError("Currently supported method: iqr.")

        threshold = _validate_number(threshold, "threshold")

        if threshold <= 0:
            raise ValueError("threshold must be positive.")

        numeric_values = sorted(
            _validate_number(value, "value")
            for value in values
        )

        if len(numeric_values) < 4:
            return _make_result(
                "outlier_detection",
                "value",
                {"outliers": [], "count": 0},
                ["At least four observations are required."]
            )

        def percentile(data: list[float], p: float) -> float:

            position = (len(data) - 1) * p
            lower = math.floor(position)
            upper = math.ceil(position)

            if lower == upper:
                return data[lower]

            return (
                data[lower] * (upper - position)
                + data[upper] * (position - lower)
            )

        q1 = percentile(numeric_values, 0.25)
        q3 = percentile(numeric_values, 0.75)

        iqr = q3 - q1

        lower_bound = q1 - threshold * iqr
        upper_bound = q3 + threshold * iqr

        outliers = [
            value
            for value in numeric_values
            if value < lower_bound or value > upper_bound
        ]

        return _make_result(
            "outlier_detection",
            "value",
            {
                "q1": round(q1, 4),
                "q3": round(q3, 4),
                "iqr": round(iqr, 4),
                "lower_bound": round(lower_bound, 4),
                "upper_bound": round(upper_bound, 4),
                "outliers": outliers,
                "count": len(outliers)
            }
        )

    except Exception as error:
        return _make_error("outlier_detection", "value", error)


# --------------------------------------------------
# 8. TREND ANALYSIS
# --------------------------------------------------

def analyze_trend(
    records: list[dict],
    time_column: str,
    value_column: str
) -> dict:

    try:
        if not records:
            return _make_result(
                "trend",
                value_column,
                {"direction": None},
                ["No records supplied."]
            )

        for record in records:

            if time_column not in record or value_column not in record:
                raise ValueError(
                    f"Missing required columns: "
                    f"{time_column} or {value_column}."
                )

        values = [
            _validate_number(record[value_column], value_column)
            for record in records
        ]

        if len(values) < 2:
            return _make_result(
                "trend",
                value_column,
                {"direction": None},
                ["At least two observations are required."]
            )

        x_values = list(range(len(values)))

        x_mean = mean(x_values)
        y_mean = mean(values)

        numerator = sum(
            (x - x_mean) * (y - y_mean)
            for x, y in zip(x_values, values)
        )

        denominator = sum(
            (x - x_mean) ** 2
            for x in x_values
        )

        slope = numerator / denominator

        predicted = [
            y_mean + slope * (x - x_mean)
            for x in x_values
        ]

        residual_sum = sum(
            (actual - estimate) ** 2
            for actual, estimate in zip(values, predicted)
        )

        total_sum = sum(
            (actual - y_mean) ** 2
            for actual in values
        )

        r_squared = (
            1 - residual_sum / total_sum
            if total_sum != 0
            else None
        )

        if slope > 0:
            direction = "increasing"
        elif slope < 0:
            direction = "decreasing"
        else:
            direction = "stable"

        change = calculate_change(
            values[0],
            values[-1],
            value_column
        )

        return _make_result(
            "trend",
            value_column,
            {
                "direction": direction,
                "slope_per_period": round(slope, 4),
                "r_squared": (
                    round(r_squared, 4)
                    if r_squared is not None
                    else None
                ),
                "first_value": values[0],
                "last_value": values[-1],
                "first_period": records[0][time_column],
                "last_period": records[-1][time_column],
                "absolute_change": change["results"]["absolute_change"],
                "percentage_change": change["results"]["percentage_change"]
            }
        )

    except Exception as error:
        return _make_error("trend", value_column, error)
