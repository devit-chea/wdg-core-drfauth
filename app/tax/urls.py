from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.tax.views.tax_view import TaxView, TaxCategoryView, EMenuTaxCategoryView

router_v1 = DefaultRouter(trailing_slash=False)
router_v1.register("tax-category", TaxCategoryView, basename="tax-category-v1")
router_v1.register("tax", TaxView, basename="tax-v1")

v1_urlpatterns = [
    # TO-DO E-Menu
    path("e-menu/tax-category/<int:pk>", EMenuTaxCategoryView.as_view()),
    path("", include(router_v1.urls)),
]

urlpatterns = [
    path("v1/", include(v1_urlpatterns)),
]
