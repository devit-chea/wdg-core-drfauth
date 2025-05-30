class CoreGenerateCode:
    prefix = None  # Must be defined in subclass
    unique_field = None  # Must be defined in subclass
    number_length = 4  # Default length, can be overridden

    def __init__(self, *args, **kwargs):
        if not self.prefix:
            raise AttributeError(f"{self.__class__.__name__} must define 'prefix'.")
        if not self.unique_field:
            raise AttributeError(
                f"{self.__class__.__name__} must define 'unique_field'."
            )
        super().__init__(*args, **kwargs)

    @classmethod
    def generate_code(
        cls,
        model,
        unique_field=None,
        prefix=None,
        number_length=None,
        branch=None,
        company=None,
    ):
        prefix = prefix or cls.prefix
        unique_field = unique_field or cls.unique_field
        number_length = number_length or cls.number_length

        if not prefix or not cls.unique_field:
            raise AttributeError(
                f"{cls.__name__} must define 'prefix' and 'unique_field'."
            )

        field = cls.unique_field
        filters = {field + "__startswith": prefix}

        if branch:
            filters["branch_id"] = branch
        if company:
            filters["company_id"] = company

        latest_entry = model.objects.filter(**filters).order_by("-" + field).first()

        if latest_entry:
            latest_code = getattr(latest_entry, field)
            latest_number = int(latest_code.replace(prefix, ""))
            next_number = latest_number + 1
        else:
            next_number = 1

        return f"{prefix}{next_number:0{number_length}d}"

    def create(self, validated_data):
        request = self.context.get("request")
        branch_id = getattr(request.user, "branch_id", None)
        company_id = getattr(request.user, "company_id", None)
        if not validated_data.get(self.unique_field):
            validated_data[self.unique_field] = self.generate_code(
                self.Meta.model, company=company_id, branch=branch_id
            )

        return super().create(validated_data)
