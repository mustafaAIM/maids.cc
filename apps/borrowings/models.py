from django.db import models, transaction
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from datetime import timedelta
from apps.core.mixins.models_mixins import TimeStampMixin

class BorrowingRecord(TimeStampMixin , models.Model ):
    """
    Model representing a book borrowing transaction.
    """
    PENDING = 'pending'
    BORROWED = 'borrowed'
    RETURNED = 'returned'
    OVERDUE = 'overdue'
    
    STATUS_CHOICES = [
        (PENDING, _('Pending')),
        (BORROWED, _('Borrowed')),
        (RETURNED, _('Returned')),
        (OVERDUE, _('Overdue')),
    ]
    
    book = models.ForeignKey('books.Book', on_delete=models.CASCADE, related_name='borrowing_records')
    patron = models.ForeignKey('patrons.Patron', on_delete=models.CASCADE, related_name='borrowing_records')
    borrow_date = models.DateTimeField(_("Borrow Date"), default=timezone.now)
    due_date = models.DateTimeField(_("Due Date"))
    return_date = models.DateTimeField(_("Return Date"), null=True, blank=True)
    status = models.CharField(_("Status"), max_length=10, choices=STATUS_CHOICES, default=PENDING)
    notes = models.TextField(_("Notes"), blank=True)
    
    class Meta:
        verbose_name = _("Borrowing Record")
        verbose_name_plural = _("Borrowing Records")
        ordering = ["-borrow_date"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["due_date"]),
        ]

    def __str__(self):
        return f"{self.book.title} borrowed by {self.patron.full_name} on {self.borrow_date.strftime('%Y-%m-%d')}"
    
    def save(self, *args, **kwargs):
        if not self.due_date:
            self.due_date = self.borrow_date + timedelta(days=14)
            
        super().save(*args, **kwargs)

    @property
    def is_overdue(self):
        """Check if the book is overdue"""
        return self.status != self.RETURNED and timezone.now() > self.due_date
