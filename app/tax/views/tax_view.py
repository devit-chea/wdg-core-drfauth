from apps.core.views import BaseModelViewSet, BaseRetrieveAPIView

from apps.tax.models.tax_model import Tax, TaxCategory
from apps.tax.serializers.tax_serializer import (
    TaxSerializer,
    TaxSaveSerializer,
    TaxCategorySerializer,
    TaxCategorySaveSerializer,
)
from apps.core.authentications import (
    CustomIsAuthenticated,
    CustomJWTStatelessUserAuthentication,
)


class EMenuTaxCategoryView(BaseRetrieveAPIView):
    model = TaxCategory
    queryset = TaxCategory.objects.all()
    serializer_class = TaxCategorySerializer
    permission_classes = [CustomIsAuthenticated]
    authentication_classes = [CustomJWTStatelessUserAuthentication]


class TaxCategoryView(BaseModelViewSet):
    model = TaxCategory
    use_branch_filter = False
    queryset = TaxCategory.objects.all()
    serializer_class = TaxCategorySaveSerializer

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return TaxCategorySerializer
        return TaxCategorySaveSerializer


class TaxView(BaseModelViewSet):
    model = Tax
    use_branch_filter = False
    queryset = Tax.objects.all()
    serializer_class = TaxSaveSerializer

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return TaxSerializer
        return TaxSaveSerializer
