from rest_framework import serializers

from apps.tax.models.tax_model import TaxCategory


class TaxCategoryLookUpMixin(serializers.ModelSerializer):
    class Meta:
        model = TaxCategory
        fields = ["id", "code", "name", "description"]
