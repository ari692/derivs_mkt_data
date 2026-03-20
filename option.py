from datetime import datetime, timezone
from decimal import Decimal

from derivs_options.option import make_option_dict
from derivs_options.pricing import option_greeks


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
    xyz_stats_today = option_greeks(
        option=xyz_option,
        underlying_price=50.0,
        r=0.0,
        b=0.0,
        volatility=0.20,
        valuation_datetime=datetime.now(timezone.utc),
    )

    print(xyz_option)
    print(f"XYZ option stats today: {xyz_stats_today}")

    xyz_option_atm_100 = make_option_dict(
        symbol="XYZ",
        strike=Decimal("100"),
        option_type="call",
        exercise_style="european",
        payout_type="standard",
        expiration=datetime(2026, 12, 26, tzinfo=timezone.utc),
    )
    xyz_stats_strike_100_spot_100 = option_greeks(
        option=xyz_option_atm_100,
        underlying_price=100.0,
        r=0.0,
        b=0.0,
        volatility=0.20,
        valuation_datetime=datetime.now(timezone.utc),
    )

    print(xyz_option_atm_100)
    print(
        "XYZ option stats today (strike=100, spot/underlying=100): "
        f"{xyz_stats_strike_100_spot_100}"
    )

    xyz_stats_strike_100_spot_100_vol_21 = option_greeks(
        option=xyz_option_atm_100,
        underlying_price=100.0,
        r=0.0,
        b=0.0,
        volatility=0.21,
        valuation_datetime=datetime.now(timezone.utc),
    )
    print(
        "XYZ option stats today (strike=100, spot/underlying=100, vol=21%): "
        f"{xyz_stats_strike_100_spot_100_vol_21}"
    )
