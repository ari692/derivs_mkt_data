from datetime import datetime
from decimal import Decimal
from typing import Any


def make_option_dict(
    symbol: str,
    strike: Decimal,
    option_type: str,
    exercise_style: str,
    payout_type: str,
    expiration: datetime,
    venue: str | None = None,
) -> dict[str, Any]:
    """Build a normalized option dictionary."""
    normalized_option_type = option_type.lower()
    normalized_exercise_style = exercise_style.lower()
    normalized_payout_type = payout_type.lower()

    if normalized_option_type not in {"call", "put"}:
        raise ValueError("option_type must be 'call' or 'put'.")
    if normalized_exercise_style not in {"european", "american"}:
        raise ValueError("exercise_style must be 'european' or 'american'.")
    if normalized_payout_type not in {"standard", "quanto"}:
        raise ValueError("payout_type must be 'standard' or 'quanto'.")
    if not isinstance(strike, Decimal):
        raise TypeError("strike must be a Decimal instance.")
    if not isinstance(expiration, datetime):
        raise TypeError("expiration must be a datetime instance.")

    option = {
        "symbol": symbol.upper(),
        "strike": strike,
        "option_type": normalized_option_type,
        "exercise_style": normalized_exercise_style,
        "payout_type": normalized_payout_type,
        "is_inverse_quanto": normalized_payout_type == "quanto",
        "expiration": expiration,
    }
    if venue is not None:
        option["venue"] = venue

    return option
