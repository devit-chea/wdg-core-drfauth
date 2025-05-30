import copy
from django.db import models, transaction
from django.core.exceptions import ValidationError
from django.db.models.deletion import ProtectedError

BASE_FIELDS = [
    "create_date",
    "write_uid",
    "create_uid",
    "write_date",
]

META_KEYS = [
    "_state",
    "active_revision",
    "previous_revision_id",
    "initial_revision_id",
] + BASE_FIELDS


class BaseTrackableModel(models.Model):
    """
    Abstract base model for timestamp and user tracking.
    Provides `create_date` and `write_date` fields.
    Overrides the `delete` method to raise a validation error for protected deletions.
    """

    create_uid = models.IntegerField(null=True, blank=True)
    write_uid = models.IntegerField(null=True, blank=True)
    branch_id = models.IntegerField(null=True, blank=True)
    company_id = models.IntegerField(null=True, blank=True)
    create_date = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    write_date = models.DateTimeField(auto_now=True, blank=True, null=True)

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False):
        """
        Overrides the delete method to handle `ProtectedError` exceptions.
        Raises a `ValidationError` if deletion is not allowed.
        """
        try:
            super().delete(using=using, keep_parents=keep_parents)
        except ProtectedError:
            raise ValidationError(
                "This record cannot be deleted as it contains references to other entities."
            )


class AbstractBaseHistory(models.Model):
    active_revision = models.BooleanField(default=True)
    force_change = models.BooleanField(default=False)
    previous_revision = models.ForeignKey(
        "self",
        on_delete=models.PROTECT,
        related_name="next_revision",
        blank=True,
        null=True,
    )
    initial_revision = models.ForeignKey(
        "self",
        on_delete=models.PROTECT,
        related_name="all_revisions",
        blank=True,
        null=True,
    )

    @transaction.atomic
    def delete(self, using=None, keep_parents=False):
        deleted = super().delete(using, keep_parents)
        self._delete_all_revision()
        return deleted

    def _delete_all_revision(self):
        if not self.initial_revision_id:
            return
        try:
            self.__class__.objects.filter(
                initial_revision__id=self.initial_revision_id
            ).delete()
        except ProtectedError as error:
            raise ValidationError(
                "It is not possible to delete this record as it contains references to other entities"
            )

    def make_force_change(self):
        self.force_change = not self.force_change
        self.save()

    def get_latest_revision(self):
        return (
            self.__class__.objects.filter(
                active_revision=True,
                initial_revision=(self.initial_revision or self.id),
            ).first()
            or self
        )

    def _is_keep_history(self, original_instances):
        try:
            enable_history_if_kwargs = getattr(
                self.__class__._meta, "enable_history_if", "__all__"
            )
            if enable_history_if_kwargs == "__all__":
                return True

            if not original_instances.filter(**enable_history_if_kwargs).exists():
                return False

            return True
        except Exception as e:
            raise Exception(
                f"invalid option: 'enable_history_if' config in {original_instances.model.__name__}.Meta:",
                e,
            )

    @transaction.atomic()
    def save(self, *args, **kwargs):
        if not self.id and self._state.adding:
            super().save(*args, **kwargs)
            return

        if not self.active_revision:
            raise ValidationError(
                f"update action isn't allow for {self.__class__.__name__}.id: {self.id}."
            )

        original_instances = self.__class__.objects.filter(pk=self.id)
        is_change, new_dict = self._try_save_or_rollback(
            original_instances, args, kwargs
        )
        if is_change:
            new_dict["create_date"] = self.write_date
            new_dict["create_uid"] = self.write_uid

            new_dict["previous_revision_id"] = self.id
            new_dict["active_revision"] = True
            if self.initial_revision:
                new_dict["initial_revision_id"] = self.initial_revision.id
            else:
                new_dict["initial_revision_id"] = self.id

            del new_dict["id"]
            clone_instance = self.__class__.objects.create(**new_dict)
            _copy_m2m_fields(self, clone_instance)
            self.id = clone_instance.id
            self.refresh_from_db()
            original_instances.update(active_revision=False)

    @transaction.atomic()
    def _try_save_or_rollback(self, original_instances, args, kwargs):
        not_keep_history_result = False, {}
        original_data = copy.deepcopy(original_instances.first().__dict__)
        super().save(*args, **kwargs)
        if not self._is_keep_history(original_instances):
            return not_keep_history_result

        update_data = copy.deepcopy(self.__dict__)

        self._pop_meta_and_exclude_field(original_data)
        self._pop_meta_and_exclude_field(update_data)

        if original_data != update_data:
            transaction.set_rollback(True)
            new_dict = copy.deepcopy(self.__dict__)
            self._pop_meta_field(new_dict)
            return True, new_dict

        return not_keep_history_result

    def _pop_meta_and_exclude_field(self, instance_dict):
        exclude_history_fields = getattr(
            self.__class__._meta, "exclude_history_fields", []
        ) + [getattr(self.__class__._meta, "sequence_numbering", "reference_no")]

        for key in META_KEYS + exclude_history_fields:
            instance_dict.pop(key, None)

    @staticmethod
    def _pop_meta_field(instance_dict):
        for key in META_KEYS:
            instance_dict.pop(key, None)

    class Meta:
        abstract = True


def _copy_m2m_fields(old_instance, new_instance):
    for field in old_instance._meta.get_fields():
        if isinstance(field, models.ManyToManyField):
            old_m2m_objs = getattr(old_instance, field.name)
            old_m2m_ids = [old_obj.id for old_obj in old_m2m_objs.all()]
            getattr(new_instance, field.name).set(old_m2m_ids)
