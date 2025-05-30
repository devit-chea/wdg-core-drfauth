class Const:
    SALE = "sale"
    PURCHASE = "purchase"
    PERCENTAGE = "percentage"
    FIXED_VALUE = "fixed_value"
    WITHHOLDING = "withholding"
    TAX_INCLUSIVE = "tax_inclusive"
    TAX_EXCLUSIVE = "tax_exclusive"
    AFTER_DISCOUNT = "after_discount"
    BEFORE_DISCOUNT = "before_discount"


class TaxConst:
    AMOUNT_TYPE = [
        (Const.PERCENTAGE, "Percentage"),
        (Const.FIXED_VALUE, "Fixed value"),
    ]

    TAX_OPTION = [
        (Const.TAX_INCLUSIVE, "Tax Inclusive"),
        (Const.TAX_EXCLUSIVE, "Tax Exclusive"),
    ]

    TAX_DISCOUNT_OPTION = [
        (Const.AFTER_DISCOUNT, "After Discount"),
        (Const.BEFORE_DISCOUNT, "Before Discount"),
    ]

    TAX_TYPE = [
        (Const.SALE, "Sale Tax"),
        (Const.PURCHASE, "Purchase Tax"),
        (Const.WITHHOLDING, "Withholding Tax"),
    ]
