from rest_framework import serializers
from apps.tax.constants.tax_const import TaxConst
from apps.core.serializers import CoreGenerateCode
from apps.tax.models.tax_model import Tax, TaxCategory
from apps.core.utils.core_date_format import core_date_format


class TaxCategorySaveSerializer(CoreGenerateCode, serializers.ModelSerializer):
    name = serializers.CharField(required=True)
    description = serializers.CharField(required=False)

    prefix = "TXC"
    number_length = 6
    unique_field = "code"

    class Meta:
        model = TaxCategory
        fields = ["id", "code", "name", "description"]


class TaxCategorySerializer(serializers.ModelSerializer):
    display_create_date = serializers.SerializerMethodField()
    display_write_date = serializers.SerializerMethodField()

    class Meta:
        model = TaxCategory
        fields = [
            "id",
            "code",
            "name",
            "description",
            "create_date",
            "write_date",
            "branch_id",
            "company_id",
            "display_create_date",
            "display_write_date",
        ]

    def get_display_create_date(self, obj):
        return core_date_format(obj.create_date)

    def get_display_write_date(self, obj):
        return core_date_format(obj.write_date)


class TaxSerializer(serializers.ModelSerializer):
    display_create_date = serializers.SerializerMethodField()
    display_write_date = serializers.SerializerMethodField()
    tax_categories = TaxCategorySaveSerializer(many=True, read_only=True)
    amount = serializers.DecimalField(
        max_digits=19,
        decimal_places=2,
        default=0,
        coerce_to_string=False,
    )

    class Meta:
        model = Tax
        fields = [
            "id",
            "code",
            "name",
            "amount",
            "amount_type",
            "type",
            "tax_option",
            "tax_discount_option",
            "is_active",
            "description",
            "tax_categories",
            "create_date",
            "write_date",
            "branch_id",
            "company_id",
            "display_create_date",
            "display_write_date",
        ]

    def get_display_create_date(self, obj):
        return core_date_format(obj.create_date)

    def get_display_write_date(self, obj):
        return core_date_format(obj.write_date)


class TaxSaveSerializer(CoreGenerateCode, serializers.ModelSerializer):
    name = serializers.CharField(required=True)
    is_active = serializers.BooleanField(default=False)
    amount_type = serializers.ChoiceField(choices=TaxConst.AMOUNT_TYPE, required=True)
    amount = serializers.DecimalField(max_digits=19, decimal_places=6, default=0)

    prefix = "TX"
    number_length = 6
    unique_field = "code"

    class Meta:
        model = Tax
        fields = "__all__"


class TaxCategoryHandleExternalSaveSerializer(
    CoreGenerateCode, serializers.ModelSerializer
):
    name = serializers.CharField(required=True)
    description = serializers.CharField(required=False)

    prefix = "TXC"
    number_length = 6
    unique_field = "code"

    class Meta:
        model = TaxCategory
        fields = [
            "id",
            "code",
            "name",
            "description",
            "company_id",
            "branch_id",
        ]


class TaxHandleExternalSaveSerializer(CoreGenerateCode, serializers.ModelSerializer):

    prefix = "TX"
    number_length = 6
    unique_field = "code"

    class Meta:
        model = Tax
        fields = [
            "id",
            "code",
            "name",
            "type",
            "amount",
            "amount_type",
            "tax_option",
            "tax_discount_option",
            "is_active",
            "description",
            "company_id",
            "branch_id",
        ]
