from django.db import models
from apps.core.abstracts import BaseTrackableModel
from apps.tax.constants.tax_const import Const, TaxConst


class TaxCategory(BaseTrackableModel):
    code = models.CharField(max_length=52, editable=False, blank=True, null=True)
    name = models.CharField(max_length=255, null=False, blank=True)
    description = models.CharField(max_length=255, blank=True)

    class Meta:
        db_table = "tax_category"


class Tax(BaseTrackableModel):
    tax_categories = models.ManyToManyField(
        TaxCategory, related_name="taxes", db_table="tax_category_tax_rel"
    )
    code = models.CharField(max_length=52, editable=False, blank=True, null=True)
    name = models.CharField(max_length=255, null=False, blank=True)
    amount = models.DecimalField(default=0, max_digits=19, decimal_places=6)
    amount_type = models.CharField(max_length=50, choices=TaxConst.AMOUNT_TYPE)

    type = models.CharField(max_length=50, choices=TaxConst.TAX_TYPE)
    tax_option = models.CharField(
        max_length=50,
        choices=TaxConst.TAX_OPTION,
        default=Const.TAX_EXCLUSIVE,
    )
    tax_discount_option = models.CharField(
        max_length=50,
        choices=TaxConst.TAX_DISCOUNT_OPTION,
        default=Const.AFTER_DISCOUNT,
    )
    is_active = models.BooleanField(default=False)
    description = models.CharField(max_length=255, blank=True)

    class Meta:
        db_table = "tax"
