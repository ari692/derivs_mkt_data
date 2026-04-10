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


def _prepare_bsm_terms(
    option: dict[str, Any],
    underlying_price: float | Decimal,
    r: float,
    b: float,
    volatility: float,
    valuation_datetime: datetime | None = None,
) -> tuple[float, float, float, float, float, float]:
    if option.get("exercise_style") != "european":
        raise ValueError("Pricing supports only european exercise_style.")
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

    return s, k, time_to_expiry, d1, d2, math.exp((b - r) * time_to_expiry)


def option_price(
    option: dict[str, Any],
    underlying_price: float | Decimal,
    r: float,
    b: float,
    volatility: float,
    valuation_datetime: datetime | None = None,
) -> float:
    """Price a European option using generalized Black-Scholes-Merton."""
    s, k, time_to_expiry, d1, d2, carry_discount = _prepare_bsm_terms(
        option=option,
        underlying_price=underlying_price,
        r=r,
        b=b,
        volatility=volatility,
        valuation_datetime=valuation_datetime,
    )
    discounted_spot = s * carry_discount
    discounted_strike = k * math.exp(-r * time_to_expiry)

    if option["option_type"] == "call":
        return discounted_spot * normal_cdf(d1) - discounted_strike * normal_cdf(d2)
    return discounted_strike * normal_cdf(-d2) - discounted_spot * normal_cdf(-d1)


def option_delta(
    option: dict[str, Any],
    underlying_price: float | Decimal,
    r: float,
    b: float,
    volatility: float,
    valuation_datetime: datetime | None = None,
) -> float:
    """Generalized BSM delta for European calls/puts."""
    _, _, _, d1, _, carry_discount = _prepare_bsm_terms(
        option=option,
        underlying_price=underlying_price,
        r=r,
        b=b,
        volatility=volatility,
        valuation_datetime=valuation_datetime,
    )
    if option["option_type"] == "call":
        return carry_discount * normal_cdf(d1)
    return carry_discount * (normal_cdf(d1) - 1.0)


def option_vega(
    option: dict[str, Any],
    underlying_price: float | Decimal,
    r: float,
    b: float,
    volatility: float,
    valuation_datetime: datetime | None = None,
) -> float:
    """Generalized BSM vega for European calls/puts."""
    s, _, time_to_expiry, d1, _, carry_discount = _prepare_bsm_terms(
        option=option,
        underlying_price=underlying_price,
        r=r,
        b=b,
        volatility=volatility,
        valuation_datetime=valuation_datetime,
    )
    return s * carry_discount * normal_pdf(d1) * math.sqrt(time_to_expiry)


def option_rho(
    option: dict[str, Any],
    underlying_price: float | Decimal,
    r: float,
    b: float,
    volatility: float,
    valuation_datetime: datetime | None = None,
) -> float:
    """Generalized BSM rho per +1.00 absolute move in rate."""
    s, k, time_to_expiry, d1, d2, carry_discount = _prepare_bsm_terms(
        option=option,
        underlying_price=underlying_price,
        r=r,
        b=b,
        volatility=volatility,
        valuation_datetime=valuation_datetime,
    )
    discounted_spot = s * carry_discount
    discounted_strike = k * math.exp(-r * time_to_expiry)

    if option["option_type"] == "call":
        return time_to_expiry * (
            discounted_strike * normal_cdf(d2) - discounted_spot * normal_cdf(d1)
        )
    return time_to_expiry * (
        discounted_spot * normal_cdf(-d1) - discounted_strike * normal_cdf(-d2)
    )


def option_theta(
    option: dict[str, Any],
    underlying_price: float | Decimal,
    r: float,
    b: float,
    volatility: float,
    valuation_datetime: datetime | None = None,
) -> float:
    """Generalized BSM theta per +1.00 day in calendar time."""
    s, k, time_to_expiry, d1, d2, carry_discount = _prepare_bsm_terms(
        option=option,
        underlying_price=underlying_price,
        r=r,
        b=b,
        volatility=volatility,
        valuation_datetime=valuation_datetime,
    )
    discounted_spot = s * carry_discount
    discounted_strike = k * math.exp(-r * time_to_expiry)
    front = -discounted_spot * normal_pdf(d1) * volatility / (2.0 * math.sqrt(time_to_expiry))

    if option["option_type"] == "call":
        theta_per_year = (
            front
            - (b - r) * discounted_spot * normal_cdf(d1)
            - r * discounted_strike * normal_cdf(d2)
        )
    else:
        theta_per_year = (
            front
            + (b - r) * discounted_spot * normal_cdf(-d1)
            + r * discounted_strike * normal_cdf(-d2)
        )
    return theta_per_year / 365.0


def option_gamma(
    option: dict[str, Any],
    underlying_price: float | Decimal,
    r: float,
    b: float,
    volatility: float,
    valuation_datetime: datetime | None = None,
) -> float:
    """Generalized BSM gamma per $1 move in underlying."""
    s, _, time_to_expiry, d1, _, carry_discount = _prepare_bsm_terms(
        option=option,
        underlying_price=underlying_price,
        r=r,
        b=b,
        volatility=volatility,
        valuation_datetime=valuation_datetime,
    )
    return carry_discount * normal_pdf(d1) / (s * volatility * math.sqrt(time_to_expiry))


def option_gamma_1pct(
    option: dict[str, Any],
    underlying_price: float | Decimal,
    r: float,
    b: float,
    volatility: float,
    valuation_datetime: datetime | None = None,
) -> float:
    """Approximate delta change for a 1% move in underlying."""
    s = float(underlying_price)
    gamma_per_1 = option_gamma(
        option=option,
        underlying_price=underlying_price,
        r=r,
        b=b,
        volatility=volatility,
        valuation_datetime=valuation_datetime,
    )
    return gamma_per_1 * s * 0.01


def option_greeks(
    option: dict[str, Any],
    underlying_price: float | Decimal,
    r: float,
    b: float,
    volatility: float,
    valuation_datetime: datetime | None = None,
) -> dict[str, float]:
    """Return price and Greeks in one call."""
    return {
        "price": option_price(
            option=option,
            underlying_price=underlying_price,
            r=r,
            b=b,
            volatility=volatility,
            valuation_datetime=valuation_datetime,
        ),
        "delta": option_delta(
            option=option,
            underlying_price=underlying_price,
            r=r,
            b=b,
            volatility=volatility,
            valuation_datetime=valuation_datetime,
        ),
        "vega": option_vega(
            option=option,
            underlying_price=underlying_price,
            r=r,
            b=b,
            volatility=volatility,
            valuation_datetime=valuation_datetime,
        ),
        "rho": option_rho(
            option=option,
            underlying_price=underlying_price,
            r=r,
            b=b,
            volatility=volatility,
            valuation_datetime=valuation_datetime,
        ),
        "theta": option_theta(
            option=option,
            underlying_price=underlying_price,
            r=r,
            b=b,
            volatility=volatility,
            valuation_datetime=valuation_datetime,
        ),
        "gamma": option_gamma(
            option=option,
            underlying_price=underlying_price,
            r=r,
            b=b,
            volatility=volatility,
            valuation_datetime=valuation_datetime,
        ),
        "gammaP": option_gamma_1pct(
            option=option,
            underlying_price=underlying_price,
            r=r,
            b=b,
            volatility=volatility,
            valuation_datetime=valuation_datetime,
        ),
    }
