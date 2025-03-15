from rest_framework.views import exception_handler
from django.core.exceptions import ValidationError as DjangoValidationError
from django.http import Http404
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework import status
from apps.core.utils.response import create_response
from django.utils.translation import gettext as _




def custom_exception_handler(exc , context):  
  """
  Custom exception handler to return a standardized response format.

  Args:
    exc: The exception that occurred
    context: The context of the request
  """
  response = exception_handler(exc, context)

  if response is None:
        if isinstance(exc, DjangoValidationError):
            data = create_response(
                success=False,
                message=_("Validation error occurred"),
                errors={"detail": exc.message},
                status_code=status.HTTP_400_BAD_REQUEST
            )
            from rest_framework.response import Response
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        return None
      
  if isinstance(exc, DRFValidationError):
      data = create_response(
            success=False,
            message=_("Validation error occurred"),
            errors=response.data if hasattr(response, 'data') else {"detail": str(exc)},
            status_code=status.HTTP_400_BAD_REQUEST
        )
      response.data = data

  elif isinstance(exc, Http404):
        data = create_response(
            success=False,
            message=_("Resource not found"),
            errors={"detail": _("Not found")},
            status_code=status.HTTP_404_NOT_FOUND
        )
        response.data = data

  else:
        data = create_response(
            success=False,
            message=str(exc),
            errors=response.data if hasattr(response, 'data') else {"detail": str(exc)},
            status_code=response.status_code
        )
        response.data = data


  return response