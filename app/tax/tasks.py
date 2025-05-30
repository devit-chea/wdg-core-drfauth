import logging
from celery import shared_task

from apps.tax.serializers.tax_serializer import (
    TaxHandleExternalSaveSerializer,
    TaxCategoryHandleExternalSaveSerializer,
)


@shared_task(name="apps.tax.handle_tax_creation")
def handle_tax_creation(event_payload):
    """To handle both Tax and Tax category from New company onboarding.

    Args:
        event_payload (dist): data prepared from "Business Service"
    """

    data = event_payload["data"]

    # Implement your Tax and Tax Category Creation Logic
    company_id = data["company_id"]
    branch_id = data["branch_id"]

    # Create Taxes
    for tax in data["tax"]:
        tax["company_id"] = company_id
        tax["branch_id"] = branch_id

        tax_serializer = TaxHandleExternalSaveSerializer(data=tax)
        if tax_serializer.is_valid(raise_exception=True):
            try:
                tax_serializer.save()
                print("Success to create Tax")
            except Exception as e:
                logging.error(f"Failed to create Tax: {str(e)}")
        else:
            logging.error(f"Failed to create Tax: {str(tax_serializer.errors)}")

    # Create Tax Categories
    for tax_category in data["tax_category"]:
        tax_category["company_id"] = company_id
        tax_category["branch_id"] = branch_id

        serializer = TaxCategoryHandleExternalSaveSerializer(data=tax_category)
        if serializer.is_valid(raise_exception=True):
            try:
                serializer.save()
                print("Success to create Tax category")
            except Exception as e:
                logging.error(f"Failed to create Tax category: {str(e)}")
        else:
            logging.error(f"Failed to create Tax category: {str(serializer.errors)}")
