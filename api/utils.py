# api/utils.py
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

def custom_exception_handler(exc, context):
    """
    Custom exception handler for API
    """
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)
    
    if response is not None:
        # Add custom error formatting
        response.data = {
            'error': {
                'code': response.status_code,
                'message': response.data.get('detail', str(exc)),
                'details': response.data
            }
        }
    
    return response


def get_view_name(view):
    """
    Custom view name function
    """
    if hasattr(view, 'get_view_name'):
        return view.get_view_name()
    
    from rest_framework.views import get_view_name as drf_get_view_name
    return drf_get_view_name(view)


def get_view_description(view, html=False):
    """
    Custom view description function
    """
    if hasattr(view, 'get_view_description'):
        return view.get_view_description(html=html)
    
    from rest_framework.views import get_view_description as drf_get_view_description
    return drf_get_view_description(view, html=html)