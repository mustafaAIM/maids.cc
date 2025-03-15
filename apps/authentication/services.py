from django.contrib.auth import get_user_model
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)
User = get_user_model()

class UserSecurityService:
    """
    Service class for security-related operations.
    Extracts security logic from views for better separation of concerns.
    """
    @staticmethod
    def handle_failed_login(email):
        """Handle failed login attempt by incrementing counter and potentially locking account"""
        try:
            user = User.objects.get(email=email)
            
            user.login_attempts += 1
            
            if user.login_attempts >= 5:
                user.locked_until = timezone.now() + timezone.timedelta(minutes=30)
                logger.warning(f"Account locked for {email} due to too many failed attempts")
            
            user.save(update_fields=['login_attempts', 'locked_until'])
            
        except User.DoesNotExist:
            pass
        except Exception as e:
            logger.error(f"Error handling failed login: {str(e)}")
        
    @staticmethod
    def reset_login_attempts(user, ip_address=None):
        """Reset login attempts and update IP after successful login"""
        try:
            if ip_address:
                user.last_login_ip = ip_address
            
            if user.login_attempts > 0:
                user.login_attempts = 0
                user.locked_until = None
                user.save(update_fields=['login_attempts', 'locked_until', 'last_login_ip'])
            elif ip_address:
                user.save(update_fields=['last_login_ip'])
                
        except Exception as e:
            logger.error(f"Error resetting login attempts: {str(e)}")





class LoginService:
    """
    Service class for login-related functionality.
    Extracts business logic from views for better separation of concerns.
    """
    @staticmethod
    def get_client_ip(request):
        """Extract client IP address from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')
    
    @staticmethod
    def check_account_locked(user):
        """Check if user account is locked and return lock information"""
        if user.is_locked:
            locked_for = max(0, int((user.locked_until - timezone.now()).total_seconds() // 60))
            return True, locked_for
        
        return False, 0
