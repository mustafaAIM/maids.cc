import logging
import time
from django.db.models.signals import pre_save, post_save, pre_delete, post_delete
from django.dispatch import receiver

model_logger = logging.getLogger('library.model')

operation_timers = {}

def log_model_operation(sender, instance, operation, **kwargs):
    """Log model operations with consistent format"""
    model_name = sender.__name__
    instance_id = getattr(instance, 'id', 'new')
    
    model_logger.info(
        f"MODEL OPERATION: {operation} {model_name} - ID: {instance_id}"
    )

@receiver(pre_save)
def track_save_start(sender, instance, **kwargs):
    if sender.__name__ in ['Book', 'Patron', 'BorrowingRecord']:
        operation_key = f"{sender.__name__}_{id(instance)}_save"
        operation_timers[operation_key] = time.time()

@receiver(post_save)
def log_save_operation(sender, instance, created, **kwargs):
    if sender.__name__ in ['Book', 'Patron', 'BorrowingRecord']:
        operation = "CREATED" if created else "UPDATED"
        log_model_operation(sender, instance, operation)
        
        operation_key = f"{sender.__name__}_{id(instance)}_save"
        if operation_key in operation_timers:
            duration = (time.time() - operation_timers[operation_key]) * 1000
            model_logger.info(
                f"MODEL OPERATION TIME: {operation} {sender.__name__} - "
                f"ID: {instance.id}, Duration: {duration:.2f}ms"
            )
            del operation_timers[operation_key]

@receiver(pre_delete)
def track_delete_start(sender, instance, **kwargs):
    if sender.__name__ in ['Book', 'Patron', 'BorrowingRecord']:
        operation_key = f"{sender.__name__}_{id(instance)}_delete"
        operation_timers[operation_key] = time.time()

@receiver(post_delete)
def log_delete_operation(sender, instance, **kwargs):
    if sender.__name__ in ['Book', 'Patron', 'BorrowingRecord']:
        log_model_operation(sender, instance, "DELETED")
        
        operation_key = f"{sender.__name__}_{id(instance)}_delete"
        if operation_key in operation_timers:
            duration = (time.time() - operation_timers[operation_key]) * 1000
            model_logger.info(
                f"MODEL OPERATION TIME: DELETE {sender.__name__} - "
                f"ID: {instance.id}, Duration: {duration:.2f}ms"
            )
            del operation_timers[operation_key]