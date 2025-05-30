SQL_LITE_DB_ALIAS = "sqlite"

DefaultViewSetActions = [
    "list",
    "create",
    "retrieve",
    "update",
    "partial_update",
    "destroy",
]


class ExcludeMetaField:
    @classmethod
    def get_exclude_field(cls):
        return [
            "create_date",
            "create_uid",
            "write_date",
            "write_uid",
        ]
