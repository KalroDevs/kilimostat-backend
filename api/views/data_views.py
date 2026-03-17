from django.db.models import Count, Avg, Sum, Q
from django.utils import timezone
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

from core.models import KilimoSTATData
from api.serializers.data_serializers import *
from api.filters.custom_filters import KilimoSTATDataFilter
from .base_views import BaseModelViewSet

class KilimoSTATDataViewSet(BaseModelViewSet):
    """
    Main ViewSet for KilimoSTATData
    """
    queryset = KilimoSTATData.objects.select_related(
        'area', 'source', 'provider', 'sector', 'subsector',
        'indicator', 'item', 'domain', 'unit', 'subgroup_dimension', 'subgroup'
    ).all()
    serializer_class = KilimoSTATDataSerializer
    filterset_class = KilimoSTATDataFilter
    search_fields = ['area__name', 'indicator__name', 'item__name', 'notes']
    ordering_fields = ['time_period', 'data_value', 'area__name', 'indicator__name']
    
    def get_serializer_class(self):
        """Use different serializers for list and detail views"""
        if self.action == 'list':
            return KilimoSTATDataListSerializer
        return KilimoSTATDataSerializer
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """
        Get summary statistics
        """
        queryset = self.filter_queryset(self.get_queryset())
        
        summary = {
            'total_records': queryset.count(),
            'total_areas': queryset.values('area').distinct().count(),
            'total_indicators': queryset.values('indicator').distinct().count(),
            'years_covered': list(queryset.values_list('time_period', flat=True).distinct().order_by('-time_period')[:10]),
            'records_by_sector': list(queryset.values('sector__name').annotate(count=Count('id')).order_by('-count')),
            'records_by_year': list(queryset.values('time_period').annotate(count=Count('id')).order_by('-time_period')[:10]),
            'latest_update': queryset.order_by('-updated_at').values_list('updated_at', flat=True).first(),
        }
        
        serializer = DataSummarySerializer(summary)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def timeseries(self, request):
        """
        Get time series data for specific indicator and area
        """
        indicator_id = request.query_params.get('indicator')
        area_id = request.query_params.get('area')
        
        if not indicator_id or not area_id:
            return Response(
                {'error': 'indicator and area parameters are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = self.queryset.filter(
            indicator_id=indicator_id,
            area_id=area_id
        ).order_by('time_period')
        
        data = [
            {
                'time_period': item.time_period,
                'value': item.data_value,
                'flag': item.flag
            }
            for item in queryset
        ]
        
        result = {
            'indicator': queryset.first().indicator.name if queryset.exists() else None,
            'area': queryset.first().area.name if queryset.exists() else None,
            'data': data
        }
        
        serializer = TimeSeriesSerializer(result)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def compare_areas(self, request):
        """
        Compare multiple areas for a given indicator and time period
        """
        indicator_id = request.query_params.get('indicator')
        time_period = request.query_params.get('time_period')
        area_ids = request.query_params.getlist('areas[]')
        
        if not indicator_id or not time_period or not area_ids:
            return Response(
                {'error': 'indicator, time_period, and areas[] parameters are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = self.queryset.filter(
            indicator_id=indicator_id,
            time_period=time_period,
            area_id__in=area_ids
        )
        
        data = [
            {
                'area_id': item.area.id,
                'area_name': item.area.name,
                'value': item.data_value
            }
            for item in queryset
        ]
        
        return Response(data)
    
    @action(detail=False, methods=['get'])
    def heatmap(self, request):
        """
        Get data for heatmap visualization
        """
        year = request.query_params.get('year')
        indicator_id = request.query_params.get('indicator')
        
        if not year or not indicator_id:
            return Response(
                {'error': 'year and indicator parameters are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = self.queryset.filter(
            indicator_id=indicator_id,
            time_period__icontains=year
        ).select_related('area')
        
        data = [
            {
                'area': item.area.name,
                'value': item.data_value,
                'latitude': item.area.latitude,
                'longitude': item.area.longitude
            }
            for item in queryset if item.area.latitude and item.area.longitude
        ]
        
        return Response(data)
    
    @action(detail=False, methods=['get'])
    def geojson(self, request):
        """
        Get data in GeoJSON format for mapping
        """
        queryset = self.filter_queryset(self.get_queryset())
        serializer = KilimoSTATDataGeoSerializer(queryset)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def latest(self, request):
        """
        Get latest data for each indicator and area
        """
        # Get distinct combinations
        combinations = self.queryset.values('indicator', 'area').distinct()
        
        latest_data = []
        for combo in combinations[:100]:  # Limit to prevent performance issues
            latest = self.queryset.filter(
                indicator_id=combo['indicator'],
                area_id=combo['area']
            ).order_by('-time_period').first()
            
            if latest:
                latest_data.append(latest)
        
        serializer = KilimoSTATDataListSerializer(latest_data, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def bulk_update(self, request):
        """
        Bulk update multiple records
        """
        data = request.data
        if not isinstance(data, list):
            return Response(
                {'error': 'Expected a list of objects'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        updated = []
        errors = []
        
        for item in data:
            try:
                instance = self.queryset.get(id=item.get('id'))
                serializer = self.get_serializer(instance, data=item, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    updated.append(serializer.data)
                else:
                    errors.append({
                        'id': item.get('id'),
                        'errors': serializer.errors
                    })
            except KilimoSTATData.DoesNotExist:
                errors.append({
                    'id': item.get('id'),
                    'error': 'Not found'
                })
        
        return Response({
            'updated': updated,
            'errors': errors
        })