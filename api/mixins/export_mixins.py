# api/mixins/export_mixins.py
import csv
import json
from django.http import HttpResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action

class ExportMixin:
    """
    Mixin to add export functionality to viewsets
    """
    
    @action(detail=False, methods=['get'], url_path='export/(?P<format>[a-z]+)')
    def export(self, request, format=None):
        """
        Export data in various formats (csv, json)
        """
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        
        if format == 'csv':
            return self._export_csv(serializer.data)
        elif format == 'json':
            return self._export_json(serializer.data)
        else:
            return Response(
                {'error': 'Unsupported format. Use csv or json'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def _export_csv(self, data):
        """Export data as CSV"""
        if not data:
            return HttpResponse(status=204)
        
        # Get field names from first item
        fieldnames = data[0].keys()
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="export.csv"'
        
        writer = csv.DictWriter(response, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
        
        return response
    
    def _export_json(self, data):
        """Export data as JSON"""
        return Response(data)


class BulkOperationsMixin:
    """
    Mixin to add bulk operations to viewsets
    """
    
    @action(detail=False, methods=['post'], url_path='bulk-create')
    def bulk_create(self, request):
        """
        Create multiple objects in one request
        """
        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        self.perform_bulk_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def perform_bulk_create(self, serializer):
        serializer.save()
    
    @action(detail=False, methods=['delete'], url_path='bulk-delete')
    def bulk_delete(self, request):
        """
        Delete multiple objects by IDs
        """
        ids = request.data.get('ids', [])
        if not ids:
            return Response(
                {'error': 'No IDs provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = self.get_queryset().filter(id__in=ids)
        count = queryset.count()
        queryset.delete()
        
        return Response(
            {'message': f'Successfully deleted {count} records'},
            status=status.HTTP_200_OK
        )