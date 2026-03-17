from rest_framework import permissions

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow admins to edit objects.
    Read-only access is allowed for any request.
    """
    def has_permission(self, request, view):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True
        # Write permissions are only allowed to admin users
        return request.user and request.user.is_staff

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True
        # Write permissions are only allowed to admin users
        return request.user and request.user.is_staff


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the owner
        # This assumes the object has a 'created_by' attribute
        if hasattr(obj, 'created_by'):
            return obj.created_by == request.user.username
        elif hasattr(obj, 'user'):
            return obj.user == request.user
        else:
            # If we can't determine ownership, default to admin only
            return request.user and request.user.is_staff


class IsStaffOrReadOnly(permissions.BasePermission):
    """
    Allow read-only access to everyone, but write access only to staff users.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff


class IsAuthenticatedAndOwner(permissions.BasePermission):
    """
    Allow access only to authenticated users who are the owners.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'created_by'):
            return obj.created_by == request.user.username
        elif hasattr(obj, 'user'):
            return obj.user == request.user
        return False


class CanExportData(permissions.BasePermission):
    """
    Permission to check if user can export data.
    """
    def has_permission(self, request, view):
        # Allow staff users to export
        if request.user and request.user.is_staff:
            return True
        
        # Check for specific permission
        if request.user and request.user.has_perm('core.can_export_data'):
            return True
            
        return False


class IsAdminOrReadOnlyForList(permissions.BasePermission):
    """
    Custom permission: Admin can do everything, others can only list/retrieve.
    """
    def has_permission(self, request, view):
        # Allow anyone to list or retrieve
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Only admin can create/update/delete
        return request.user and request.user.is_staff


class DjangoModelPermissionsWithRead(permissions.DjangoModelPermissions):
    """
    The request is authenticated using `django.contrib.auth` permissions.
    Add read permissions for authenticated users.
    """
    perms_map = {
        'GET': ['%(app_label)s.view_%(model_name)s'],
        'OPTIONS': ['%(app_label)s.view_%(model_name)s'],
        'HEAD': ['%(app_label)s.view_%(model_name)s'],
        'POST': ['%(app_label)s.add_%(model_name)s'],
        'PUT': ['%(app_label)s.change_%(model_name)s'],
        'PATCH': ['%(app_label)s.change_%(model_name)s'],
        'DELETE': ['%(app_label)s.delete_%(model_name)s'],
    }


class IsAdminOrAuthenticatedReadOnly(permissions.BasePermission):
    """
    Allow authenticated users to read, only admins can write.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
            
        if request.method in permissions.SAFE_METHODS:
            return True
            
        return request.user.is_staff