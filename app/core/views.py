import ast
import operator
from typing import Any
from functools import reduce
from django.db.models import Q
from django.db import transaction
from rest_framework.exceptions import APIException
from rest_framework.permissions import IsAuthenticated
from django.contrib.contenttypes.models import ContentType
from rest_framework import filters, generics, viewsets, serializers
from apps.core.utils.core_utils import get_model_fields_only, separate_value
from rest_framework_simplejwt.authentication import JWTStatelessUserAuthentication
from apps.core.abstracts import AbstractBaseHistory


class DefaultOrdering(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        q_ordering = request.query_params.get("ordering")

        if not q_ordering or q_ordering == "-":
            model = queryset.model
            model_fields = [f.name for f in model._meta.fields]

            # Step 1: Try 'id'
            if "id" in model_fields:
                ordering_field = "id"
            # Step 2: Fallback to 'create_date' if 'id' doesn't exist
            elif "create_date" in model_fields:
                ordering_field = "create_date"
            else:
                # Final fallback to primary key
                ordering_field = model._meta.pk.name

            queryset = queryset.order_by(f"-{ordering_field}")

        return queryset


class CustomOrdering(filters.OrderingFilter):
    def filter_queryset(self, request, queryset, view):
        return validate_mode_field_ordering(self, request, queryset, view)


def filter_revision_if_need(queryset):
    if issubclass(queryset.model, AbstractBaseHistory):
        return queryset.filter(active_revision=True)

    return queryset


def validate_mode_field_ordering(self, request, queryset, view):
    ordering = self.get_ordering(request, queryset, view)

    if not ordering:
        ordering = []
    q_ordering = request.query_params.get("ordering")
    if q_ordering:
        field_list = [field.strip() for field in q_ordering.split(",")]
        related_orderings = format_value(q_ordering)
        ordering = ordering + related_orderings
        ordering = sort_index(field_list, ordering)
        model = queryset.model.objects
        queryset = model.prefetch_related().distinct().order_by(*ordering)

    return queryset


def format_value(q_ordering):
    related_orderings = []
    if "," in q_ordering:
        related_orderings = [
            q_order for q_order in q_ordering.split(",") if "__" in q_order
        ]
    else:
        if "__" in q_ordering:
            related_orderings = [q_ordering]
    return related_orderings


def sort_index(index1, index2):
    new_index = []
    for field in index1:
        if field in index2:
            new_index.append(field)
    for field in index2:
        if field not in new_index:
            new_index.append(field)
    return new_index


class CompanyFilter(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        model = getattr(view, "model", None)
        if not model:
            return queryset

        content_type = ContentType.objects.filter(model=model.__name__.lower()).first()
        if not content_type:
            return queryset

        model_class = content_type.model_class()
        if not model_class:
            return queryset

        related_company_field = None
        for field in model_class._meta.fields:
            if (
                field.get_internal_type() in ("ForeignKey", "ManyToManyField")
                and field.name == "company"
                or field.name == "company_id"
            ):
                related_company_field = field

        if related_company_field:
            queryset = queryset.filter(
                **{related_company_field.name: request.user.company_id}
            )

        return queryset


class BranchFilter(filters.BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
        if view.use_branch_filter:
            model = getattr(view, "model", None)
            if not model:
                return queryset

            content_type = ContentType.objects.filter(
                model=model.__name__.lower()
            ).first()
            if not content_type:
                return queryset

            model_class = content_type.model_class()
            if not model_class:
                return queryset

            related_branch_field = None
            for field in model_class._meta.fields:
                if (
                    field.get_internal_type() in ("ForeignKey", "ManyToManyField")
                    and field.name == "branch"
                    or field.name == "branch_id"
                ):
                    related_branch_field = field
            if related_branch_field:
                queryset = queryset.filter(
                    **{related_branch_field.name: request.user.branch_id}
                )

        return queryset


class FilterByID(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        if request.query_params.get("id"):
            return queryset.filter(pk=request.query_params.get("id"))
        return queryset


class SearchFields(filters.BaseFilterBackend):
    """
    Search field in table
    default search all field"""

    def filter_queryset(self, request, queryset, view):
        if request.query_params and isinstance(request.query_params, dict):
            search = request.query_params.get("search")
            scopes = request.query_params.get("scopes")
            model = view.model
            if not search:
                return queryset
            if scopes:
                search_fields = self.__separate_scope(scopes)
                expr = self._get_search_expression(search, search_fields)
                queryset = self._get_queryset_filter(queryset, model, expr)
            elif hasattr(view, "search_fields") and view.search_fields:
                expr = self._get_search_expression(search, view.search_fields)
                queryset = self._get_queryset_filter(queryset, model, expr)
            else:
                search_fields = get_model_fields_only(model)
                expr = self._get_search_expression(search, search_fields)
                queryset = self._get_queryset_filter(queryset, model, expr)

        return queryset

    def __separate_scope(self, scopes):
        if isinstance(scopes, str):
            search_fields = scopes.split(",")
            return search_fields
        return None

    def _get_queryset_filter(self, queryset, model, expr):
        try:
            # if model == User:
            #     queryset = (
            #         queryset.annotate(
            #             fullname=Concat("first_name", Value(" "), "last_name")
            #         )
            #         .filter(expr)
            #         .distinct()
            #     )
            # else:
            queryset = queryset.filter(expr)
        except Exception as e:
            raise serializers.ValidationError(e)
        return queryset

    def _get_search_expression(self, query, search_fields):
        if isinstance(query, str):
            query = query.strip()
        expr = reduce(
            operator.or_,
            (
                (
                    Q(**{f"fullname__icontains": query})
                    if search_field == "fullname"
                    else Q(**{f"{search_field}__icontains": query})
                )
                for search_field in search_fields
            ),
        )
        return expr


class FilterFields(filters.BaseFilterBackend):
    """global filter backend with model fields"""

    def filter_queryset(self, request, queryset, view):
        _queryset = queryset
        q_params = request.query_params
        build_in_params = [
            "page",
            "page_size",
            "search",
            "ordering",
            "isSortAsc",
            "sortBy",
            "scopes",
        ]
        new_exp = []

        try:
            if view.model and q_params and isinstance(q_params, dict):
                param_dict = dict(q_params.copy())
                for param_key, param_values in param_dict.items():
                    if param_key in build_in_params:
                        continue

                    if param_values is None:
                        continue

                    param_list = (
                        param_values
                        if isinstance(param_values, list)
                        else [param_values]
                    )
                    for param_value in param_list:
                        try:
                            value, expression = separate_value(param_value)
                            if not expression:
                                expression = "equal"
                            expr = self._get_search_expression(
                                expression, value, param_key
                            )

                            if self._is_filterable(queryset, expr):
                                new_exp.append(expr)

                        except Exception:
                            pass

                if new_exp:
                    ex = reduce(operator.and_, new_exp)
                    queryset = queryset.filter(ex)
        except Exception:
            return filter_revision_if_need(_queryset)
        return filter_revision_if_need(queryset)

    def _is_filterable(self, queryset, exp):
        """try to filter the expression before load them in to main query"""
        try:
            queryset.filter(exp).first()
            return True
        except Exception:
            return False

    def _get_search_expression(self, expression, value, search_field):
        expr = ""
        match expression:
            case "like":
                expression = "icontains"
                expr = self.get_condition(search_field, expression, value)
            case "equal":
                expr = self.get_condition(search_field, expression, value, False)
            case "lte":
                expr = self.get_condition(search_field, expression, value, False)
            case "gte":
                expr = self.get_condition(search_field, expression, value, False)
            case "lt":
                expr = self.get_condition(search_field, expression, value, False)
            case "gt":
                expr = self.get_condition(search_field, expression, value, False)
            case "not_equal":
                expr = self.get_condition(search_field, expression, value, True)
            case "is_set":
                expression = "isnull"
                expr = self.get_condition(search_field, expression, False)
            case "is_not_set":
                expression = "isnull"
                expr = self.get_condition(search_field, expression, True)
            case "not_like":
                expression = "icontains"
                expr = self.get_condition(search_field, expression, value, is_not=True)
            case "in":
                expression = "in"
                value = ast.literal_eval(value)
                expr = self.get_condition(search_field, expression, value, is_not=False)
            case "not_in":
                expression = "in"
                value = ast.literal_eval(value)
                expr = self.get_condition(search_field, expression, value, is_not=True)
            case _:
                expr = self.get_condition(search_field, "icontains", value)
        return expr

    def get_condition(self, search_field, expression, value, is_not=False):
        new_expression = f"__{expression}"

        if expression == "equal" or expression == "not_equal":
            new_expression = ""

        condition = Q(**{f"{search_field}{new_expression}": value})
        if is_not:
            condition = ~condition
        return condition


class BaseModelViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTStatelessUserAuthentication]
    permission_classes = [IsAuthenticated]
    filter_backends = [
        DefaultOrdering,
        CustomOrdering,
        FilterByID,
        CompanyFilter,
        BranchFilter,
        SearchFields,
        FilterFields,
    ]

    use_branch_filter = True
    filterset_fields = ordering_fields = "__all__"

    def _assign_user_fields(self, serializer, fields_mapping):
        """Assign user-related fields if they exist in the model."""
        request = self.request
        model = serializer.context.get("view").model
        if not request or not model:
            return

        # Get actual model field names
        model_field_names = {
            field.name
            for field in model._meta.get_fields()
            if not field.auto_created or field.concrete
        }

        for field, user_attr in fields_mapping.items():
            if field in model_field_names:
                serializer.validated_data[field] = getattr(request, user_attr, None)
            else:
                # Ensure it's not accidentally left in validated_data
                serializer.validated_data.pop(field, None)

    def perform_create(self, serializer):
        """Assign company details during object creation."""
        with transaction.atomic():
            try:
                self._assign_user_fields(
                    serializer,
                    {
                        "create_uid": "user_id",
                        "branch_id": "branch_id",
                        "company_id": "company_id",
                    },
                )
                serializer.save()
            except Exception as e:
                raise APIException(str(e))

    def perform_update(self, serializer):
        """Ensure company details remain assigned during updates."""
        with transaction.atomic():
            try:
                self._assign_user_fields(
                    serializer,
                    {
                        "write_uid": "user_id",
                        "branch_id": "branch_id",
                        "company_id": "company_id",
                    },
                )
                serializer.save()
            except Exception as e:
                raise APIException(str(e))


class BaseRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):
    def perform_update(self, serializer):
        request = self.request
        if not hasattr(request, "user_id") and not hasattr(request, "company_id"):
            raise ValueError("Unauthorized")

        model = serializer.context.get("view").model
        if hasattr(model, "write_uid"):
            serializer.validated_data["write_uid"] = getattr(request, "user_id", None)

        serializer.save()


class BaseUpdateAPIView(generics.UpdateAPIView):
    def perform_update(self, serializer):
        model = serializer.context.get("view").model
        if hasattr(model, "write_uid"):
            serializer.validated_data["write_uid"] = getattr(
                self.request, "user_id", None
            )
        serializer.save()


class BaseRetrieveAPIView(generics.RetrieveAPIView):
    use_branch_filter: bool = False

    def get_queryset(self) -> Any:
        """
        Override get_queryset to filter list view by company_id.
        """
        branch_id = getattr(self.request, "branch_id", None)
        company_id = getattr(self.request, "company_id", None)

        filters = {"company_id": company_id}
        if self.use_branch_filter and branch_id is not None:
            filters["branch_id"] = branch_id

        return super().get_queryset().filter(**filters)


class CoreListAPIView(generics.ListAPIView):
    authentication_classes = [JWTStatelessUserAuthentication]
    permission_classes = [IsAuthenticated]
    filter_backends = [
        DefaultOrdering,
        CustomOrdering,
        FilterByID,
        CompanyFilter,
        BranchFilter,
        SearchFields,
        FilterFields,
    ]
    use_branch_filter = True
    filterset_fields = ordering_fields = "__all__"


class BaseCreateAPIView(generics.CreateAPIView):
    pass


class BaseRetrieveDestroyAPIView(generics.RetrieveDestroyAPIView):
    pass


class BaseDestroyAPIView(generics.DestroyAPIView):
    pass
