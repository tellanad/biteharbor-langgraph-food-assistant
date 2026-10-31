"""Deterministic business rules and customer-scoped data access."""

import re
from typing import Any

from biteharbor.data.menu import MENU_ITEMS
from biteharbor.data.orders import ORDERS_DB

IDENTIFIER_PATTERN = re.compile(
    r"\bORD-\d+\b|\bBH\d+TRK\b|\b[\w.+-]+@[\w.-]+\.[A-Z]{2,}\b",
    re.IGNORECASE,
)


def extract_identifier(text: str) -> str | None:
    """Extract an order ID, tracking ID, or email from untrusted user text."""
    match = IDENTIFIER_PATTERN.search(text)
    return match.group(0) if match else None


def filter_menu(query: str) -> list[dict[str, Any]]:
    """Enforce exact cuisine, dietary, price, and availability constraints."""
    normalized = query.casefold()
    price_match = re.search(r"(?:under|below|less than)\s*(?:rs\.?|inr|₹)?\s*(\d+)", normalized)
    cuisine = next(
        (name for name in ("indian", "italian", "american", "fusion") if name in normalized),
        None,
    )
    required_tags: set[str] = set()
    if "vegan" in normalized:
        required_tags.add("vegan")
    elif re.search(r"\b(?:veg|vegetarian)\b", normalized):
        required_tags.add("vegetarian")
    if "gluten-free" in normalized or "gluten free" in normalized:
        required_tags.add("gluten-free")

    results = []
    for item in MENU_ITEMS:
        tags = set(item["dietary_tags"])
        if "vegan" in tags:
            tags.add("vegetarian")
        if not item["available"]:
            continue
        if cuisine and item["cuisine"].casefold() != cuisine:
            continue
        if price_match and item["price"] >= int(price_match.group(1)):
            continue
        if not required_tags.issubset(tags):
            continue
        results.append(dict(item))
    return results


def lookup_order(identifier: str, customer_id: str) -> dict[str, Any]:
    """Return only an order owned by the trusted caller identity.

    Nonexistent and unauthorized identifiers intentionally return the same response.
    """
    normalized = identifier.casefold()
    for order in ORDERS_DB.values():
        searchable = {
            order["order_id"].casefold(),
            order["tracking_id"].casefold(),
            order["customer_email"].casefold(),
        }
        if normalized in searchable and order["customer_id"] == customer_id:
            return {
                "order_id": order["order_id"],
                "item_id": order["item_id"],
                "item_name": order["item_name"],
                "status": order["status"],
                "price": order["price"],
                "order_date": order["order_date"],
                "estimated_delivery": order["estimated_delivery"],
                "tracking_id": order["tracking_id"],
            }
    return {"error": "No matching order was found for this customer."}
