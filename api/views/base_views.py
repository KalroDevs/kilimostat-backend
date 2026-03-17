from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters as drf_filters

from api.pagination.custom_pagination import StandardResultsSetPagination
from api.permissions.custom_permissions import IsAdminOrReadOnly, CanExportData
from api.mixins.export_mixins import ExportMixin, BulkOperationsMixin

class BaseModelViewSet(viewsets.ModelViewSet, ExportMixin, BulkOperationsMixin):
    """
    Base viewset for all models with common functionality
    """
    permission_classes = [IsAdminOrReadOnly]  # Now this should work
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, drf_filters.SearchFilter, drf_filters.OrderingFilter]
    
    @action(detail=False, methods=['get'])
    def counts(self, request):
        """
        Get count of records
        """
        count = self.get_queryset().count()
        return Response({'count': count})
    
    @action(detail=False, methods=['get'])
    def distinct_values(self, request):
        """
        Get distinct values for a field
        """
        field = request.query_params.get('field')
        if not field:
            return Response({'error': 'field parameter required'}, status=400)
        
        values = self.get_queryset().values_list(field, flat=True).distinct()
        return Response(list(values))


class BaseReadOnlyViewSet(mixins.RetrieveModelMixin,
                          mixins.ListModelMixin,
                          viewsets.GenericViewSet,
                          ExportMixin):
    """
    Base viewset for read-only access
    """
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, drf_filters.SearchFilter, drf_filters.OrderingFilter]