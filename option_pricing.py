from datetime import datetime, timezone
from decimal import Decimal
import math
from typing import Any


def normal_pdf(x: float) -> float:
    """Standard normal probability density function."""
    return math.exp(-0.5 * x * x) / math.sqrt(2.0 * math.pi)


def normal_cdf(x: float) -> float:
    """Standard normal cumulative distribution function."""
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def _to_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def option_price(
    option: dict[str, Any],
    underlying_price: float | Decimal,
    r: float,
    b: float,
    volatility: float,
    valuation_datetime: datetime | None = None,
) -> float:
    """Price a European option using the generalized Black-Scholes-Merton model.

    Formula (Garman-Kohlhagen style carry adjustment):
      Call = S*exp((b-r)T)*N(d1) - K*exp(-rT)*N(d2)
      Put  = K*exp(-rT)*N(-d2) - S*exp((b-r)T)*N(-d1)
      d1   = [ln(S/K) + (b + 0.5*sigma^2)T] / [sigma*sqrt(T)]
      d2   = d1 - sigma*sqrt(T)
    """
    if option.get("exercise_style") != "european":
        raise ValueError("option_price supports only european exercise_style.")
    if option.get("option_type") not in {"call", "put"}:
        raise ValueError("option['option_type'] must be 'call' or 'put'.")
    if volatility <= 0.0:
        raise ValueError("volatility must be positive.")

    expiration = option.get("expiration")
    if not isinstance(expiration, datetime):
        raise TypeError("option['expiration'] must be a datetime instance.")

    now = _to_utc(valuation_datetime or datetime.now(timezone.utc))
    expiry = _to_utc(expiration)
    time_to_expiry = (expiry - now).total_seconds() / (365.0 * 24.0 * 60.0 * 60.0)
    if time_to_expiry <= 0.0:
        raise ValueError("option expiration must be in the future.")

    strike = option.get("strike")
    if isinstance(strike, Decimal):
        k = float(strike)
    else:
        k = float(strike)
    s = float(underlying_price)
    if s <= 0.0 or k <= 0.0:
        raise ValueError("underlying_price and strike must be positive.")

    sigma_sqrt_t = volatility * math.sqrt(time_to_expiry)
    d1 = (
        math.log(s / k) + (b + 0.5 * volatility * volatility) * time_to_expiry
    ) / sigma_sqrt_t
    d2 = d1 - sigma_sqrt_t

    discounted_spot = s * math.exp((b - r) * time_to_expiry)
    discounted_strike = k * math.exp(-r * time_to_expiry)

    if option["option_type"] == "call":
        return discounted_spot * normal_cdf(d1) - discounted_strike * normal_cdf(d2)
    return discounted_strike * normal_cdf(-d2) - discounted_spot * normal_cdf(-d1)
