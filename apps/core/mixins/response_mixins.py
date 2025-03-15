from rest_framework.response import Response
from ..utils.response import create_response


class ResponseMixin:
    """Mixin to standardize response formats across views."""
    
    def send_response(self, data=None, message="", status=200, success=True, errors=None):
        """
        Send a standardized response.
        """
        response_data = create_response(
            success=success,
            message=message,
            data=data,
            errors=errors,
            status_code=status
        )
        return Response(response_data, status=status)

    def send_success_response(self, data=None, message="Success", status=200):
        """
        Send a success response.
        """
        return self.send_response(data=data, message=message, status=status)

    def send_error_response(self, message="Error", errors=None, status=400):
        """
        Send an error response.
        """
        return self.send_response(
            message=message,
            errors=errors,
            status=status,
            success=False
        )