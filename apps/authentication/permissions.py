from rest_framework import permissions


class IsLibrarian(permissions.BasePermission):
    """
    Permission check for librarian role.
    """
    message = "You must be a librarian to perform this action."
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_librarian


class IsPatron(permissions.BasePermission):
    """
    Permission check for patron role.
    """
    message = "You must be a patron to perform this action."
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_patron


class IsUserSelf(permissions.BasePermission):
    """
    Permission check for user acting on their own account.
    """
    message = "You can only perform this action on your own account."
    
    def has_object_permission(self, request, view, obj):
        return obj.id == request.user.id