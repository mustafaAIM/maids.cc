from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.core.mixins.models_mixins import TimeStampMixin, SoftDeleteMixin, SoftDeleteManager, AllObjectsManager


class PatronManager(SoftDeleteManager):
    """Custom manager for Patron model."""
    pass


class Patron(TimeStampMixin, SoftDeleteMixin):
    """
    Model representing a library patron/member.
    """
    user = models.OneToOneField(
        'authentication.User', 
        on_delete=models.SET_NULL, 
        related_name='patron_profile',
        null=True, 
        blank=True
    )
    
    first_name = models.CharField(_("First Name"), max_length=100)
    last_name = models.CharField(_("Last Name"), max_length=100)
    email = models.EmailField(_("Email"), unique=True)
    phone_number = models.CharField(_("Phone Number"), max_length=15, blank=True)
    membership_date = models.DateField(_("Membership Date"), auto_now_add=True)
    
    address = models.TextField(_("Address"), blank=True)
    birth_date = models.DateField(_("Birth Date"), null=True, blank=True)
    
    active = models.BooleanField(_("Active"), default=True)
    member_id = models.CharField(_("Member ID"), max_length=20, unique=True)
    
    objects = PatronManager()
    all_objects = AllObjectsManager()
    
    class Meta:
        verbose_name = _("Patron")
        verbose_name_plural = _("Patrons")
        ordering = ["last_name", "first_name"]
        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["member_id"]),
            models.Index(fields=["last_name", "first_name"]),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.member_id})"

    @property
    def full_name(self):
        """Return the patron's full name"""
        return f"{self.first_name} {self.last_name}"
    
    # @property
    # def has_active_loans(self):
    #     return self.borrowing_records.filter(
    #         status__in=['pending', 'borrowed', 'overdue']
    #     ).exists()
    
    # def get_recent_borrowings(self, limit=5):
    #     return self.borrowing_records.order_by('-borrow_date')[:limit]
