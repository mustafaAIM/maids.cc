import time
import logging
import traceback
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
import uuid

exception_logger = logging.getLogger('library.exception')
request_logger = logging.getLogger('library.request')

class RequestLoggingMiddleware(MiddlewareMixin):
    """
    Middleware to log all incoming requests and their processing time.
    """
    
    def process_request(self, request):
        request.start_time = time.time()
        
        request.request_id = str(uuid.uuid4())
        
        user = request.user.email if hasattr(request, 'user') and request.user.is_authenticated else 'Anonymous'
        
        request_logger.info(
            f"[{request.request_id}] Request started: {request.method} {request.path} - "
            f"User: {user}, IP: {self.get_client_ip(request)}"
        )
        
    def process_response(self, request, response):
        if hasattr(request, 'start_time'):
            duration = (time.time() - request.start_time) * 1000
            
            request_logger.info(
                f"[{getattr(request, 'request_id', 'Unknown')}] Request finished: "
                f"{request.method} {request.path} - "
                f"Status: {response.status_code}, Duration: {duration:.2f}ms"
            )
            
            if duration > 1000:
                request_logger.warning(
                    f"[{getattr(request, 'request_id', 'Unknown')}] SLOW RESPONSE: "
                    f"{request.method} {request.path} - Duration: {duration:.2f}ms"
                )
                
        return response
    
    def process_exception(self, request, exception):
        request_id = getattr(request, 'request_id', 'Unknown')
        exception_logger.error(
            f"[{request_id}] Unhandled exception in {request.method} {request.path}: "
            f"{type(exception).__name__}: {str(exception)}"
        )
        
        if settings.DEBUG:
            exception_logger.error(
                f"[{request_id}] Stack trace:\n{traceback.format_exc()}"
            )
            
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')