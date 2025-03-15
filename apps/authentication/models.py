from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from apps.core.mixins.models_mixins import TimeStampMixin, SoftDeleteMixin, SoftDeleteManager, AllObjectsManager


class UserManager(BaseUserManager, SoftDeleteManager):
    """Custom manager for User model with additional methods for user creation."""
    
    def create_user(self, email, password=None, **extra_fields):
        """
        Create and save a User with the given email and password.
        """
        if not email:
            raise ValueError(_('Users must have an email address'))
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('role', User.ROLE_LIBRARIAN)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin, TimeStampMixin, SoftDeleteMixin):
    """
    Custom User model that uses email as the unique identifier
    instead of username and incorporates soft delete functionality.
    """
    # Role choices
    ROLE_PATRON = 'patron'
    ROLE_LIBRARIAN = 'librarian'
    
    ROLE_CHOICES = (
        (ROLE_PATRON, _('Patron')),
        (ROLE_LIBRARIAN, _('Librarian')),
    )
    
    email = models.EmailField(_('Email Address'), unique=True)
    first_name = models.CharField(_('First Name'), max_length=30, blank=True)
    last_name = models.CharField(_('Last Name'), max_length=150, blank=True)
    role = models.CharField(_('Role'), max_length=10, choices=ROLE_CHOICES, default=ROLE_PATRON)
    is_active = models.BooleanField(_('Active'), default=True)
    is_staff = models.BooleanField(_('Staff Status'), default=False)
    date_joined = models.DateTimeField(_('Date Joined'), default=timezone.now)
    
    # Security-related fields
    last_login_ip = models.GenericIPAddressField(_('Last Login IP'), null=True, blank=True)
    login_attempts = models.PositiveIntegerField(_('Login Attempts'), default=0)
    locked_until = models.DateTimeField(_('Locked Until'), null=True, blank=True)
    
    # Use custom managers
    objects = UserManager()
    all_objects = AllObjectsManager()
    
    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = []  
    
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name=_('groups'),
        blank=True,
        help_text=_(
            'The groups this user belongs to. A user will get all permissions '
            'granted to each of their groups.'
        ),
        related_name='custom_user_set',
        related_query_name='custom_user',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name=_('user permissions'),
        blank=True,
        help_text=_('Specific permissions for this user.'),
        related_name='custom_user_set',
        related_query_name='custom_user',
    )
    
    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        
    def __str__(self):
        return self.email
    
    def get_full_name(self):
        """Return the user's full name."""
        return f"{self.first_name} {self.last_name}".strip() or self.email
    
    def get_short_name(self):
        """Return the user's short name."""
        return self.first_name or self.email.split('@')[0]
    
    @property
    def is_locked(self):
        """Check if the user account is locked."""
        if self.locked_until and self.locked_until > timezone.now():
            return True
        return False
    
    @property
    def is_librarian(self):
        """Check if the user is a librarian."""
        return self.role == self.ROLE_LIBRARIAN
    
    @property
    def is_patron(self):
        """Check if the user is a patron."""
        return self.role == self.ROLE_PATRON

    def increment_login_attempts(self):
        """Increment login attempts and lock account if threshold reached."""
        self.login_attempts += 1
        
        # Lock account after 5 failed attempts for 30 minutes
        if self.login_attempts >= 5:
            self.locked_until = timezone.now() + timezone.timedelta(minutes=30)
        
        # Important: Save the changes
        self.save(update_fields=['login_attempts', 'locked_until'])
    
    def reset_login_attempts(self):
        """Reset login attempts after successful login."""
        if self.login_attempts > 0:
            self.login_attempts = 0
            self.locked_until = None
            self.save(update_fields=['login_attempts', 'locked_until'])