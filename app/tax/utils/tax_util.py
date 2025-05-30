from decimal import Decimal, InvalidOperation
from apps.core.utils.core_number import wdg_rounding


def find_percentage(*, price: Decimal, fixed_value: Decimal) -> Decimal:
    try:
        if price <= 0:
            return Decimal(price)
        if price < fixed_value:
            raise ValueError("Price cannot be smaller than the fixed value.")
        return (fixed_value / price) * 100
    except (InvalidOperation, ValueError) as e:
        raise ValueError(f"Invalid input: {e}")


def find_fixed_value(*, price: Decimal, percentage: Decimal) -> Decimal:
    try:
        if price <= 0:
            return Decimal(0)
        if not (0 <= percentage <= 100):
            raise ValueError("Percentage must be between 0 and 100.")
        return (price * percentage) / 100
    except (InvalidOperation, ValueError) as e:
        raise ValueError(f"Invalid input: {e}")


class CambodiaTaxCalculator:
    def __init__(self, base_price, tax_rates, discount=0):
        """
        base_price: Decimal
        tax_rates: List of dict
        discount: Decimal
        """
        self.base_price = Decimal(base_price)
        self.tax_rates = tax_rates
        self.discount = Decimal(discount)

    def apply_discount(self, price, tax_discount_option):
        if tax_discount_option == "before_discount":
            return price
        elif tax_discount_option == "after_discount":
            return price - self.discount
        else:
            raise ValueError("Invalid tax discount option.")

    def calculate_tax(self):
        tax_details = {}
        total_tax = Decimal(0)
        final_price = self.base_price - self.discount

        for tax in self.tax_rates:
            name = tax["name"]
            amount = Decimal(tax["amount"])
            amount_type = tax["amount_type"]
            tax_option = tax["tax_option"]
            tax_discount_option = tax["tax_discount_option"]

            price_for_tax = self.apply_discount(self.base_price, tax_discount_option)

            if tax_option == "tax_exclusive":
                if amount_type == "percentage":
                    tax_amount = find_fixed_value(
                        price=price_for_tax, percentage=amount
                    )
                else:  # fixed_value
                    tax_amount = amount
                final_price += tax_amount

            elif tax_option == "tax_inclusive":
                if amount_type == "percentage":
                    tax_base = price_for_tax / (1 + (amount / 100))
                    tax_amount = price_for_tax - tax_base
                else:  # fixed_value
                    tax_amount = amount
                # final_price already includes tax, no add

            else:
                raise ValueError("Invalid tax option.")

            total_tax += tax_amount
            tax_details[name] = tax_amount

        return {
            "base_price": self.base_price,
            "final_price": final_price,
            "total_tax": total_tax,
            "tax_breakdown": tax_details,
        }
