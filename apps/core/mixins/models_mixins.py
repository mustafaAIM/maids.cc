from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class TimeStampMixin(models.Model):
    """
    Mixin that provides created_at and updated_at fields.
    """
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated At"), auto_now=True)

    class Meta:
        abstract = True


class SoftDeleteMixin(models.Model):
    """
    Mixin that provides soft delete functionality.
    Instead of actually deleting the object, it is marked as deleted.
    """
    is_deleted = models.BooleanField(_("Deleted"), default=False)
    deleted_at = models.DateTimeField(_("Deleted At"), null=True, blank=True)

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False):
        """
        Soft delete the model instance by setting is_deleted=True
        and recording when it was deleted.
        """
        if not self.is_deleted:
            self.is_deleted = True
            self.deleted_at = timezone.now()
            self.save(using=using)
        
    def hard_delete(self, using=None, keep_parents=False):
        """
        Permanently delete the model instance.
        """
        return super().delete(using=using, keep_parents=keep_parents)


class SoftDeleteManager(models.Manager):
    """
    Manager that excludes deleted objects by default.
    """
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


class AllObjectsManager(models.Manager):
    """
    Manager that includes deleted objects.
    """
    def get_queryset(self):
        return super().get_queryset()