from django.utils.translation import gettext_lazy as _
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from apps.core.mixins.response_mixins import ResponseMixin
from apps.core.aspects.decorators import log_method_call, measure_performance
from apps.authentication.permissions import IsLibrarian
from .models import Patron
from .serializers import PatronSerializer
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page 
from django.views.decorators.vary import vary_on_headers


class PatronViewSet(ResponseMixin, viewsets.ModelViewSet):
    """
    ViewSet for patron management operations.
    """
    queryset = Patron.objects.all()
    serializer_class = PatronSerializer
    permission_classes = [IsAuthenticated, IsLibrarian]
    
    def get_permissions(self):
        """
        Override to allow patrons to view patron details but only librarians 
        to modify them.
        """
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsLibrarian()]
    
    @log_method_call("List Patrons")
    @measure_performance("List Patrons Performance")
    @method_decorator(vary_on_headers('Authorization'))
    @method_decorator(cache_page(timeout=60 * 5))
    def list(self, request, *args, **kwargs):
        """List all patrons n"""
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return self.send_success_response(
            data=serializer.data,
            message=_("Patrons retrieved successfully")
        )
    
    @log_method_call("Retrieve Patron")
    @measure_performance("Retrieve Patron Performance")
    @method_decorator(vary_on_headers('Authorization'))
    @method_decorator(cache_page(timeout=60 * 5))
    def retrieve(self, request, *args, **kwargs):
        """Retrieve a specific patron"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return self.send_success_response(
            data=serializer.data,
            message=_("Patron details retrieved successfully")
        )
    
    @log_method_call("Create Patron")
    @measure_performance("Create Patron Performance")
    def create(self, request, *args, **kwargs):
        """Create a new patron"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return self.send_success_response(
            data=serializer.data,
            message=_("Patron created successfully"),
            status=status.HTTP_201_CREATED
        )
    
    @log_method_call("Update Patron")
    @measure_performance("Update Patron Performance")
    def update(self, request, *args, **kwargs):
        """Update an existing patron"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return self.send_success_response(
            data=serializer.data,
            message=_("Patron updated successfully")
        )
    
    @log_method_call("Delete Patron")
    def destroy(self, request, *args, **kwargs):
        """Soft delete a patron"""
        instance = self.get_object()
        
        # if instance.has_active_loans:
        #     return self.send_error_response(
        #         message=_("Cannot delete patron with active loans"),
        #         status=status.HTTP_400_BAD_REQUEST
        #     )
            
        instance.hard_delete()
        return self.send_success_response(
            message=_("Patron deleted successfully"),
            status=status.HTTP_204_NO_CONTENT
        )
    
  