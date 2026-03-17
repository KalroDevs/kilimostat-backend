from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination
from rest_framework.response import Response
from collections import OrderedDict

class StandardResultsSetPagination(PageNumberPagination):
    """
    Standard pagination for API endpoints
    """
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 1000
    
    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('count', self.page.paginator.count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('total_pages', self.page.paginator.num_pages),
            ('current_page', self.page.number),
            ('results', data)
        ]))


class LargeResultsSetPagination(PageNumberPagination):
    """
    Pagination for large datasets
    """
    page_size = 200
    page_size_query_param = 'page_size'
    max_page_size = 5000


class CustomLimitOffsetPagination(LimitOffsetPagination):
    """
    Limit-offset pagination for flexible queries
    """
    default_limit = 50
    max_limit = 1000