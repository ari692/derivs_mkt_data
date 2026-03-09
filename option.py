from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

from option_pricing import option_price


def make_option_dict(
    symbol: str,
    strike: Decimal,
    option_type: str,
    exercise_style: str,
    payout_type: str,
    expiration: datetime,
    venue: str | None = None,
) -> dict[str, Any]:
    """Build a normalized option dictionary.

    Parameters
    ----------
    symbol:
        Underlying symbol (for example, BTC).
    strike:
        Strike price as a Decimal.
    option_type:
        "call" or "put".
    exercise_style:
        "european" or "american".
    payout_type:
        "standard" or "quanto" (inverse).
    expiration:
        Option expiration as a datetime instance.
    venue:
        Optional venue name (for example, Deribit).
    """
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


if __name__ == "__main__":
    option = make_option_dict(
        symbol="BTC",
        strike=Decimal("100000"),
        option_type="call",
        exercise_style="european",
        payout_type="standard",
        expiration=datetime(2026, 12, 25, 8, 0, 0),
        venue="Deribit",
    )
    print(option)

    xyz_option = make_option_dict(
        symbol="XYZ",
        strike=Decimal("50"),
        option_type="call",
        exercise_style="european",
        payout_type="standard",
        expiration=datetime(2026, 12, 26, tzinfo=timezone.utc),
    )
    xyz_price_today = option_price(
        option=xyz_option,
        underlying_price=50.0,
        r=0.0,
        b=0.0,
        volatility=0.20,
        valuation_datetime=datetime.now(timezone.utc),
    )

    print(xyz_option)
    print(f"XYZ option price today: {xyz_price_today:.6f}")

    xyz_option_atm_100 = make_option_dict(
        symbol="XYZ",
        strike=Decimal("100"),
        option_type="call",
        exercise_style="european",
        payout_type="standard",
        expiration=datetime(2026, 12, 26, tzinfo=timezone.utc),
    )
    xyz_price_strike_100_spot_100 = option_price(
        option=xyz_option_atm_100,
        underlying_price=100.0,
        r=0.0,
        b=0.0,
        volatility=0.20,
        valuation_datetime=datetime.now(timezone.utc),
    )

    print(xyz_option_atm_100)
    print(
        "XYZ option price today (strike=100, spot/underlying=100): "
        f"{xyz_price_strike_100_spot_100:.6f}"
    )
