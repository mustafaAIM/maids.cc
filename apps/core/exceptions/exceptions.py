from rest_framework.exceptions import APIException
from rest_framework import status
from django.utils.translation import gettext_lazy as _


class BaseCustomException(APIException):
    default_detail = _('An error occurred')
    default_code = 'error'

    def __init__(self, detail=None, code=None):
        if detail is None:
            detail = self.default_detail
        if code is None:
            code = self.default_code
        super().__init__(detail, code)


class ValidationError(BaseCustomException):
    default_detail = _('Invalid data')
    default_code = 'invalid'
    status_code = status.HTTP_400_BAD_REQUEST


class NotFoundError(BaseCustomException):
    default_detail = _('Resource not found')
    default_code = 'not_found'
    status_code = status.HTTP_404_NOT_FOUND


class PermissionDeniedError(BaseCustomException):
    default_detail = _('Permission denied')
    default_code = 'permission_denied'
    status_code = status.HTTP_403_FORBIDDEN


class ConflictError(BaseCustomException):
    default_detail = _('Resource conflict')
    default_code = 'conflict'
    status_code = status.HTTP_409_CONFLICT


class ThrottledError(BaseCustomException):
    default_detail = _('Throttled')
    default_code = 'throttled'
    status_code = status.HTTP_429_TOO_MANY_REQUESTS

