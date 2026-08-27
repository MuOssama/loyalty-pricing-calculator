"""
core.py
--------
Core math for the loyalty / hesitation-discount pricing model.

Scenario:
    A merchant sells a product at a normal price T (e.g. $200), and a
    returning/loyal client is offered a lower target price K (e.g. $190).
    Instead of jumping straight to the discount (which risks the client
    "gaming" the offer and never becoming a real repeat buyer), the
    merchant ramps the price down gradually over N orders, so order
    number x pays price P_x.

Two ramp shapes are supported:

    Normal / Linear:
        T(x) = T - [2 * (T - K) * (x - 1)] / (N - 1)

    Exponential (base 2):
        P_x = T - (T - K) * N * (2**(x - 1) - 1) / (2**N - N - 1)

    Note: with these formulas the two ramps do NOT behave identically at
    the endpoints:
        - Normal:      x = 1 -> T   |   x = N -> 2K - T  (overshoots past K)
        - Exponential: x = 1 -> T   |   average of all orders = K

Special case: N == 1 means there is only a single order, so it is just
priced at T (there's no ramp to speak of, and both formulas divide by
N - 1 or would need N - x with N == x == 1).
"""

from dataclasses import dataclass
from typing import List, Literal, Union

Method = Literal["normal", "exponential"]


def normal_price(T: float, K: float, N: int, x: int) -> float:
    """Linear ramp price for order number x."""
    if N <= 1:
        return T
    return T - (2 * (T - K) * (x - 1)) / (N - 1)


def exponential_price(T: float, K: float, N: int, x: int) -> float:
    """Exponential ramp price for order number x."""
    if N <= 1:
        return T
    return T - (T - K) * N * (2 ** (x - 1) - 1) / (2 ** N - N - 1)


@dataclass
class Row:
    order: Union[int, str]
    normal_price: float = None
    normal_discount_pct: float = None
    normal_savings: float = None
    exponential_price: float = None
    exponential_discount_pct: float = None
    exponential_savings: float = None


def validate_inputs(T: float, K: float, N: int) -> List[str]:
    """Return a list of human readable warnings (empty list == all good)."""
    warnings = []
    if N < 1:
        raise ValueError("N (number of orders) must be at least 1.")
    if T <= 0:
        raise ValueError("T (normal price) must be greater than 0.")
    if K < 0:
        raise ValueError("K (target discounted price) cannot be negative.")
    if K > T:
        warnings.append(
            f"K (${K:.2f}) is greater than T (${T:.2f}) - price will increase "
            f"over time instead of decreasing."
        )
    if N == 1:
        warnings.append(
            "N = 1: there is only one order, so it is simply priced at T. "
            "K is not used."
        )
    return warnings


def generate_table(T: float, K: float, N: int, method: str = "both") -> List[Row]:
    """
    Build the pricing table for orders 1..N.

    method: "normal", "exponential", or "both"
    """
    rows: List[Row] = []
    
    sum_normal_price = 0.0
    sum_normal_savings = 0.0
    sum_exponential_price = 0.0
    sum_exponential_savings = 0.0

    for x in range(1, N + 1):
        row = Row(order=x)
        if method in ("normal", "both"):
            p = normal_price(T, K, N, x)
            row.normal_price = round(p, 2)
            row.normal_discount_pct = round((T - p) / T * 100, 2) if T else 0.0
            row.normal_savings = round(T - p, 2)
            
            sum_normal_price += p
            sum_normal_savings += (T - p)
            
        if method in ("exponential", "both"):
            p = exponential_price(T, K, N, x)
            row.exponential_price = round(p, 2)
            row.exponential_discount_pct = round((T - p) / T * 100, 2) if T else 0.0
            row.exponential_savings = round(T - p, 2)
            
            sum_exponential_price += p
            sum_exponential_savings += (T - p)
            
        rows.append(row)

    # Add Summary Row
    summary = Row(order="Avg / Total")
    if method in ("normal", "both"):
        avg_p = sum_normal_price / N if N else 0
        summary.normal_price = round(avg_p, 2)
        summary.normal_discount_pct = round((T - avg_p) / T * 100, 2) if T else 0.0
        summary.normal_savings = round(sum_normal_savings, 2)
        
    if method in ("exponential", "both"):
        avg_p = sum_exponential_price / N if N else 0
        summary.exponential_price = round(avg_p, 2)
        summary.exponential_discount_pct = round((T - avg_p) / T * 100, 2) if T else 0.0
        summary.exponential_savings = round(sum_exponential_savings, 2)
        
    rows.append(summary)

    return rows


def columns_for_method(method: str):
    """Return (header_labels, row_attr_names) matching the chosen method(s)."""
    headers = ["Order #"]
    attrs = ["order"]
    if method in ("normal", "both"):
        headers += ["Normal Price", "Normal Discount %", "Normal Savings"]
        attrs += ["normal_price", "normal_discount_pct", "normal_savings"]
    if method in ("exponential", "both"):
        headers += ["Exponential Price", "Exponential Discount %", "Exponential Savings"]
        attrs += ["exponential_price", "exponential_discount_pct", "exponential_savings"]
    return headers, attrs


def rows_to_table(rows: List[Row], method: str):
    """Convert Row objects into a list of lists matching columns_for_method."""
    headers, attrs = columns_for_method(method)
    table = []
    for r in rows:
        line = []
        for a in attrs:
            val = getattr(r, a)
            if a == "order":
                line.append(str(val))
            elif val is None:
                line.append("")
            elif "pct" in a:
                line.append(f"{val:.2f}%")
            else:
                line.append(f"${val:.2f}")
        table.append(line)
    return headers, table
