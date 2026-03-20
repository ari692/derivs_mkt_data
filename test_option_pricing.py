from datetime import datetime, timedelta, timezone
from decimal import Decimal
import math
import unittest

from option import make_option_dict
from option_pricing import (
    normal_cdf,
    normal_pdf,
    option_delta,
    option_price,
    option_vega,
)


class TestNormalDistributionRoutines(unittest.TestCase):
    def test_normal_pdf_at_zero(self) -> None:
        expected = 1.0 / math.sqrt(2.0 * math.pi)
        self.assertAlmostEqual(normal_pdf(0.0), expected, places=12)

    def test_normal_pdf_is_symmetric(self) -> None:
        self.assertAlmostEqual(normal_pdf(1.5), normal_pdf(-1.5), places=12)

    def test_normal_cdf_at_zero(self) -> None:
        self.assertAlmostEqual(normal_cdf(0.0), 0.5, places=12)

    def test_normal_cdf_symmetry_identity(self) -> None:
        x = 1.2
        self.assertAlmostEqual(normal_cdf(-x), 1.0 - normal_cdf(x), places=12)


class TestGeneralizedBSMOptionPrice(unittest.TestCase):
    def setUp(self) -> None:
        self.valuation_datetime = datetime(2026, 1, 1, tzinfo=timezone.utc)
        self.expiration = self.valuation_datetime + timedelta(days=365)

    def test_call_price_matches_known_black_scholes_value(self) -> None:
        option = make_option_dict(
            symbol="BTC",
            strike=Decimal("100"),
            option_type="call",
            exercise_style="european",
            payout_type="standard",
            expiration=self.expiration,
        )
        price = option_price(
            option=option,
            underlying_price=100.0,
            r=0.05,
            b=0.05,
            volatility=0.2,
            valuation_datetime=self.valuation_datetime,
        )
        self.assertAlmostEqual(price, 10.4506, places=4)

    def test_put_price_matches_known_black_scholes_value(self) -> None:
        option = make_option_dict(
            symbol="BTC",
            strike=Decimal("100"),
            option_type="put",
            exercise_style="european",
            payout_type="standard",
            expiration=self.expiration,
        )
        price = option_price(
            option=option,
            underlying_price=100.0,
            r=0.05,
            b=0.05,
            volatility=0.2,
            valuation_datetime=self.valuation_datetime,
        )
        self.assertAlmostEqual(price, 5.5735, places=4)

    def test_generalized_put_call_parity(self) -> None:
        call_option = make_option_dict(
            symbol="BTC",
            strike=Decimal("100"),
            option_type="call",
            exercise_style="european",
            payout_type="quanto",
            expiration=self.expiration,
        )
        put_option = make_option_dict(
            symbol="BTC",
            strike=Decimal("100"),
            option_type="put",
            exercise_style="european",
            payout_type="quanto",
            expiration=self.expiration,
        )

        s = 110.0
        r = 0.03
        b = 0.01
        sigma = 0.25
        t = 1.0

        call_price = option_price(
            option=call_option,
            underlying_price=s,
            r=r,
            b=b,
            volatility=sigma,
            valuation_datetime=self.valuation_datetime,
        )
        put_price = option_price(
            option=put_option,
            underlying_price=s,
            r=r,
            b=b,
            volatility=sigma,
            valuation_datetime=self.valuation_datetime,
        )

        rhs = s * math.exp((b - r) * t) - 100.0 * math.exp(-r * t)
        self.assertAlmostEqual(call_price - put_price, rhs, places=10)

    def test_rejects_american_exercise(self) -> None:
        option = make_option_dict(
            symbol="BTC",
            strike=Decimal("100"),
            option_type="call",
            exercise_style="american",
            payout_type="standard",
            expiration=self.expiration,
        )
        with self.assertRaises(ValueError):
            option_price(
                option=option,
                underlying_price=100.0,
                r=0.05,
                b=0.05,
                volatility=0.2,
                valuation_datetime=self.valuation_datetime,
            )


class TestGeneralizedBSMGreeks(unittest.TestCase):
    def setUp(self) -> None:
        self.valuation_datetime = datetime(2026, 1, 1, tzinfo=timezone.utc)
        self.expiration = self.valuation_datetime + timedelta(days=365)

    def test_call_delta_matches_known_black_scholes_value(self) -> None:
        option = make_option_dict(
            symbol="XYZ",
            strike=Decimal("100"),
            option_type="call",
            exercise_style="european",
            payout_type="standard",
            expiration=self.expiration,
        )
        delta = option_delta(
            option=option,
            underlying_price=100.0,
            r=0.05,
            b=0.05,
            volatility=0.2,
            valuation_datetime=self.valuation_datetime,
        )
        self.assertAlmostEqual(delta, 0.6368306512, places=10)

    def test_put_delta_matches_known_black_scholes_value(self) -> None:
        option = make_option_dict(
            symbol="XYZ",
            strike=Decimal("100"),
            option_type="put",
            exercise_style="european",
            payout_type="standard",
            expiration=self.expiration,
        )
        delta = option_delta(
            option=option,
            underlying_price=100.0,
            r=0.05,
            b=0.05,
            volatility=0.2,
            valuation_datetime=self.valuation_datetime,
        )
        self.assertAlmostEqual(delta, -0.3631693488, places=10)

    def test_generalized_delta_parity(self) -> None:
        call_option = make_option_dict(
            symbol="XYZ",
            strike=Decimal("100"),
            option_type="call",
            exercise_style="european",
            payout_type="standard",
            expiration=self.expiration,
        )
        put_option = make_option_dict(
            symbol="XYZ",
            strike=Decimal("100"),
            option_type="put",
            exercise_style="european",
            payout_type="standard",
            expiration=self.expiration,
        )
        r = 0.05
        b = 0.02
        call_delta = option_delta(
            option=call_option,
            underlying_price=105.0,
            r=r,
            b=b,
            volatility=0.25,
            valuation_datetime=self.valuation_datetime,
        )
        put_delta = option_delta(
            option=put_option,
            underlying_price=105.0,
            r=r,
            b=b,
            volatility=0.25,
            valuation_datetime=self.valuation_datetime,
        )
        self.assertAlmostEqual(call_delta - put_delta, math.exp((b - r) * 1.0), places=10)

    def test_vega_matches_known_black_scholes_value(self) -> None:
        option = make_option_dict(
            symbol="XYZ",
            strike=Decimal("100"),
            option_type="call",
            exercise_style="european",
            payout_type="standard",
            expiration=self.expiration,
        )
        vega = option_vega(
            option=option,
            underlying_price=100.0,
            r=0.05,
            b=0.05,
            volatility=0.2,
            valuation_datetime=self.valuation_datetime,
        )
        self.assertAlmostEqual(vega, 37.5240346917, places=8)

    def test_vega_same_for_call_and_put(self) -> None:
        call_option = make_option_dict(
            symbol="XYZ",
            strike=Decimal("100"),
            option_type="call",
            exercise_style="european",
            payout_type="standard",
            expiration=self.expiration,
        )
        put_option = make_option_dict(
            symbol="XYZ",
            strike=Decimal("100"),
            option_type="put",
            exercise_style="european",
            payout_type="standard",
            expiration=self.expiration,
        )
        call_vega = option_vega(
            option=call_option,
            underlying_price=105.0,
            r=0.03,
            b=0.01,
            volatility=0.25,
            valuation_datetime=self.valuation_datetime,
        )
        put_vega = option_vega(
            option=put_option,
            underlying_price=105.0,
            r=0.03,
            b=0.01,
            volatility=0.25,
            valuation_datetime=self.valuation_datetime,
        )
        self.assertAlmostEqual(call_vega, put_vega, places=12)

    def test_vega_matches_finite_difference(self) -> None:
        option = make_option_dict(
            symbol="XYZ",
            strike=Decimal("100"),
            option_type="call",
            exercise_style="european",
            payout_type="standard",
            expiration=self.expiration,
        )
        sigma = 0.20
        h = 1e-4
        price_up = option_price(
            option=option,
            underlying_price=100.0,
            r=0.05,
            b=0.05,
            volatility=sigma + h,
            valuation_datetime=self.valuation_datetime,
        )
        price_down = option_price(
            option=option,
            underlying_price=100.0,
            r=0.05,
            b=0.05,
            volatility=sigma - h,
            valuation_datetime=self.valuation_datetime,
        )
        vega_fd = (price_up - price_down) / (2.0 * h)
        vega = option_vega(
            option=option,
            underlying_price=100.0,
            r=0.05,
            b=0.05,
            volatility=sigma,
            valuation_datetime=self.valuation_datetime,
        )
        self.assertAlmostEqual(vega, vega_fd, places=6)


if __name__ == "__main__":
    unittest.main()
