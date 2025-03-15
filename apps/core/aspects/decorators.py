import time
import functools
import logging
import uuid
from django.conf import settings

method_logger = logging.getLogger('library.method')
performance_logger = logging.getLogger('library.performance')
transaction_logger = logging.getLogger('library.transaction')

def generate_request_id():
    """Generate a unique ID for request tracing"""
    return str(uuid.uuid4())

def log_method_call(method_name=None):
    """
    Decorator to log method calls with parameters and return values.
    
    Usage:
    @log_method_call("Book Creation")
    def create_book(self, serializer):
        # method body
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            actual_method_name = method_name or func.__qualname__
            
            call_id = generate_request_id()
            
            arg_names = func.__code__.co_varnames[1:func.__code__.co_argcount]
            arg_values = args[1:] if len(args) > 0 else []
            all_args = dict(zip(arg_names, arg_values))
            all_args.update(kwargs)
            
            filtered_args = {k: v for k, v in all_args.items() 
                            if k not in ['password', 'token']}
            
            method_logger.info(
                f"[{call_id}] ENTER: {actual_method_name} - Args: {filtered_args}"
            )
            
            try:
                result = func(*args, **kwargs)
                method_logger.info(
                    f"[{call_id}] EXIT: {actual_method_name} - Success"
                )
                return result
                
            except Exception as e:
                method_logger.error(
                    f"[{call_id}] ERROR: {actual_method_name} - {type(e).__name__}: {str(e)}"
                )
                raise
                
        return wrapper
    return decorator

def measure_performance(method_name=None):
    """
    Decorator to measure and log execution time of methods.
    
    Usage:
    @measure_performance("Book Search")
    def search_books(self, request):
        # method body
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            actual_method_name = method_name or func.__qualname__
            
            call_id = generate_request_id()
            
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                execution_time = (time.time() - start_time) * 1000
                performance_logger.info(
                    f"[{call_id}] PERFORMANCE: {actual_method_name} - "
                    f"Execution time: {execution_time:.2f}ms"
                )
                
                if execution_time > 500:
                    performance_logger.warning(
                        f"[{call_id}] SLOW EXECUTION: {actual_method_name} - "
                        f"Execution time: {execution_time:.2f}ms"
                    )
                    
        return wrapper
    return decorator

def log_transaction(transaction_type):
    """
    Decorator to log business transactions (borrowing, returning, etc.)
    
    Usage:
    @log_transaction("BOOK_BORROW")
    def borrow_book(self, book_id, patron_id):
        # method body
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            user = None
            request = args[1] if len(args) > 1 and hasattr(args[1], 'user') else None
            if request and hasattr(request, 'user') and request.user.is_authenticated:
                user = request.user.email
                
            transaction_id = generate_request_id()
            
            transaction_logger.info(
                f"[{transaction_id}] {transaction_type} STARTED - "
                f"User: {user}, Args: {kwargs}"
            )
            
            try:
                result = func(*args, **kwargs)
                
                transaction_logger.info(
                    f"[{transaction_id}] {transaction_type} COMPLETED - Success"
                )
                
                return result
                
            except Exception as e:
                transaction_logger.error(
                    f"[{transaction_id}] {transaction_type} FAILED - "
                    f"{type(e).__name__}: {str(e)}"
                )
                raise
                
        return wrapper
    return decorator