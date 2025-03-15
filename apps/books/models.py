from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from apps.core.mixins.models_mixins import TimeStampMixin, SoftDeleteMixin, SoftDeleteManager


class BookManager(SoftDeleteManager):
    """Custom manager for Book model"""
    pass

class Book(TimeStampMixin, SoftDeleteMixin, models.Model):
    """Model representing a book in the library system."""
    
    title = models.CharField(_("Title"), max_length=255)
    author = models.CharField(_("Author"), max_length=255)
    isbn = models.CharField(_("ISBN"), max_length=13, unique=True)
    publication_year = models.PositiveIntegerField(_("Publication Year"), null=True, blank=True)
    publisher = models.CharField(_("Publisher"), max_length=255, blank=True)
    description = models.TextField(_("Description"), blank=True)
    available_copies = models.PositiveIntegerField(_("Available Copies"), default=1)
    total_copies = models.PositiveIntegerField(_("Total Copies"), default=1)
    
    objects = BookManager()
    
    class Meta:
        verbose_name = _("Book")
        verbose_name_plural = _("Books")
        ordering = ["title"]
        indexes = [
            models.Index(fields=["isbn"]),
            models.Index(fields=["author"]),
        ]

    def __str__(self):
        return f"{self.title} by {self.author} ({self.isbn})"

    @property
    def is_available(self):
        """Check if at least one copy is available for borrowing"""
        return self.available_copies > 0

    def save(self, *args, **kwargs):
        if not self.pk:
            self.available_copies = self.total_copies
        super().save(*args, **kwargs)
