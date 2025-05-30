from decimal import Decimal, ROUND_HALF_UP
from apps.core.utils.core_utils import to_decimal


def wdg_rounding(value: Decimal, rounding: int = 2):
    rounding_factor = Decimal(f"1e-{rounding}")
    return value.quantize(rounding_factor, rounding=ROUND_HALF_UP)


def wdg_number_format(value: Decimal, rounding: int = 2, precision: int = 2):
    rounded = wdg_rounding(value, rounding)
    return f"{rounded:,.{precision}f}"


def wdg_currency_format(
    value: Decimal,
    currency: str,
    symbol_position="before",
    rounding: int = 2,
    precision: int = 2,
):
    currency_symbols = {"USD": "$", "KHR": "៛"}
    symbol = currency_symbols.get(currency, "")

    precision = 0 if currency == "KHR" else precision
    formatted_amount = wdg_number_format(value, rounding, precision)

    if symbol_position == "after":
        return f"{formatted_amount}{symbol}"
    return f"{symbol}{formatted_amount}"
