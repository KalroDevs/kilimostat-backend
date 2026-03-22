from rest_framework import serializers
from rest_framework import viewsets, filters, generics, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Q, Avg, Min, Max
from django.utils import timezone
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiExample, inline_serializer
from drf_spectacular.types import OpenApiTypes

from core.models import KilimoSTATData, DataProvider, Indicator, Area, Sector, Metadata
from api.serializers import (
    KilimoSTATDataSerializer, KilimoSTATDataDetailSerializer,
    StatisticsSerializer
)
from api.filters import KilimoSTATDataFilter


# ============================================================================
# KILIMOSTAT DATA VIEWSET
# ============================================================================

@extend_schema_view(
    list=extend_schema(
        summary="List all data records",
        description="Returns a paginated list of all KilimoSTAT data records with optional filtering",
        tags=['data'],
        parameters=[
            OpenApiParameter(name='area_id', type=int, location=OpenApiParameter.QUERY, description='Filter by area ID'),
            OpenApiParameter(name='indicator_id', type=int, location=OpenApiParameter.QUERY, description='Filter by indicator ID'),
            OpenApiParameter(name='sector_id', type=int, location=OpenApiParameter.QUERY, description='Filter by sector ID'),
            OpenApiParameter(name='time_period', type=str, location=OpenApiParameter.QUERY, description='Filter by exact time period'),
            OpenApiParameter(name='time_period_min', type=str, location=OpenApiParameter.QUERY, description='Filter by minimum time period'),
            OpenApiParameter(name='time_period_max', type=str, location=OpenApiParameter.QUERY, description='Filter by maximum time period'),
            OpenApiParameter(name='flag', type=str, location=OpenApiParameter.QUERY, description='Filter by data flag'),
            OpenApiParameter(name='is_active', type=bool, location=OpenApiParameter.QUERY, description='Filter by active status'),
        ],
    ),
    retrieve=extend_schema(
        summary="Retrieve a data record",
        description="Returns detailed information about a specific data record including metadata",
        tags=['data'],
    ),
    create=extend_schema(
        summary="Create a new data record",
        description="Creates a new KilimoSTAT data record",
        tags=['data'],
        request=KilimoSTATDataSerializer,
        responses={201: KilimoSTATDataSerializer},
    ),
    update=extend_schema(
        summary="Update a data record",
        description="Updates an existing data record",
        tags=['data'],
        request=KilimoSTATDataSerializer,
    ),
    partial_update=extend_schema(
        summary="Partially update a data record",
        description="Updates selected fields of an existing data record",
        tags=['data'],
        request=KilimoSTATDataSerializer,
    ),
    destroy=extend_schema(
        summary="Delete a data record",
        description="Deletes a data record (soft delete not implemented - use is_active=False instead)",
        tags=['data'],
    ),
)
class KilimoSTATDataViewSet(viewsets.ModelViewSet):
    """ViewSet for KilimoSTATData model"""
    queryset = KilimoSTATData.objects.all().select_related(
        'area', 'source', 'provider', 'sector', 'subsector',
        'indicator', 'item', 'domain', 'unit', 'subgroup_dimension', 'subgroup'
    ).prefetch_related('metadata')
    serializer_class = KilimoSTATDataSerializer
    filterset_class = KilimoSTATDataFilter
    search_fields = ['notes', 'slug', 'area__name', 'indicator__name']
    ordering_fields = ['time_period', 'data_value', 'created_at', 'area__name']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return KilimoSTATDataDetailSerializer
        return KilimoSTATDataSerializer
    
    @extend_schema(
        summary="Get data by area",
        description="Returns all data records for a specific area",
        tags=['data'],
        parameters=[
            OpenApiParameter(name='area_id', type=int, required=True, location=OpenApiParameter.QUERY, description='Area ID to filter by'),
        ],
        responses={200: KilimoSTATDataSerializer(many=True)},
        examples=[
            OpenApiExample(
                'Valid Request',
                value={'area_id': 1},
                request_only=True,
            ),
        ],
    )
    @action(detail=False, methods=['get'])
    def by_area(self, request):
        """Group data by area"""
        area_id = request.query_params.get('area_id')
        if not area_id:
            return Response(
                {'error': 'area_id parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        data = self.queryset.filter(area_id=area_id, is_active=True)
        serializer = self.get_serializer(data, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        summary="Get data by indicator",
        description="Returns all data records for a specific indicator",
        tags=['data'],
        parameters=[
            OpenApiParameter(name='indicator_id', type=int, required=True, location=OpenApiParameter.QUERY, description='Indicator ID to filter by'),
        ],
        responses={200: KilimoSTATDataSerializer(many=True)},
        examples=[
            OpenApiExample(
                'Valid Request',
                value={'indicator_id': 1},
                request_only=True,
            ),
        ],
    )
    @action(detail=False, methods=['get'])
    def by_indicator(self, request):
        """Group data by indicator"""
        indicator_id = request.query_params.get('indicator_id')
        if not indicator_id:
            return Response(
                {'error': 'indicator_id parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        data = self.queryset.filter(indicator_id=indicator_id, is_active=True)
        serializer = self.get_serializer(data, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        summary="Get timeseries data",
        description="Returns timeseries data for a specific indicator and area",
        tags=['data'],
        parameters=[
            OpenApiParameter(name='indicator_id', type=int, required=True, location=OpenApiParameter.QUERY, description='Indicator ID'),
            OpenApiParameter(name='area_id', type=int, required=True, location=OpenApiParameter.QUERY, description='Area ID'),
        ],
        responses={
            200: inline_serializer(
                name='TimeseriesResponse',
                fields={
                    'year': serializers.CharField(),
                    'value': serializers.FloatField(),
                    'flag': serializers.CharField(),
                    'unit': serializers.CharField(),
                }
            )},
        examples=[
            OpenApiExample(
                'Valid Request',
                value={'indicator_id': 1, 'area_id': 1},
                request_only=True,
            ),
            OpenApiExample(
                'Response Example',
                value=[
                    {'year': '2020', 'value': 4500000, 'flag': 'official', 'unit': 'MT'},
                    {'year': '2021', 'value': 4800000, 'flag': 'official', 'unit': 'MT'},
                ],
                response_only=True,
            ),
        ],
    )
    @action(detail=False, methods=['get'])
    def timeseries(self, request):
        """Get timeseries data for a specific indicator and area"""
        indicator_id = request.query_params.get('indicator_id')
        area_id = request.query_params.get('area_id')
        
        if not indicator_id or not area_id:
            return Response(
                {'error': 'indicator_id and area_id parameters are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        data = self.queryset.filter(
            indicator_id=indicator_id,
            area_id=area_id,
            is_active=True
        ).order_by('time_period')
        
        result = [
            {
                'year': d.time_period,
                'value': d.data_value,
                'flag': d.flag,
                'unit': d.unit.symbol or d.unit.name
            }
            for d in data
        ]
        
        return Response(result)
    
    @extend_schema(
        summary="Get data summary",
        description="Returns summary statistics for all data records",
        tags=['data'],
        responses={
            200: inline_serializer(
                name='SummaryResponse',
                fields={
                    'total_records': serializers.IntegerField(),
                    'date_range': serializers.DictField(child=serializers.CharField()),
                    'by_sector': serializers.ListField(child=serializers.DictField()),
                    'by_area_level': serializers.ListField(child=serializers.DictField()),
                    'average_value': serializers.FloatField(allow_null=True),
                }
            ),
        },
    )
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get summary statistics"""
        queryset = self.queryset.filter(is_active=True)
        
        summary = {
            'total_records': queryset.count(),
            'date_range': {
                'min': queryset.aggregate(Min('time_period'))['time_period__min'],
                'max': queryset.aggregate(Max('time_period'))['time_period__max']
            },
            'by_sector': list(queryset.values('sector__name').annotate(
                count=Count('id')
            ).order_by('-count')[:10]),
            'by_area_level': list(queryset.values('area__administrative_level').annotate(
                count=Count('id')
            )),
            'average_value': queryset.aggregate(Avg('data_value'))['data_value__avg']
        }
        
        return Response(summary)


# ============================================================================
# STATISTICS VIEW - FIXED
# ============================================================================

@extend_schema(
    summary="Get system statistics",
    description="Returns overall statistics about the KilimoSTAT system including counts and distributions",
    tags=['statistics'],
    responses={200: StatisticsSerializer()},
    examples=[
        OpenApiExample(
            'Response Example',
            value={
                'total_records': 15000,
                'total_providers': 45,
                'total_indicators': 120,
                'total_areas': 290,
                'date_range': {'min': '2010', 'max': '2023'},
                'top_sectors': [
                    {'name': 'Agriculture', 'record_count': 5000},
                    {'name': 'Livestock', 'record_count': 3500},
                ],
                'quality_distribution': {
                    'excellent': 5000,
                    'good': 4000,
                    'fair': 3000,
                    'poor': 2000,
                    'unassessed': 1000,
                },
                'recent_uploads': [
                    {'id': 123, 'indicator__name': 'Maize Production', 'area__name': 'Nairobi', 'time_period': '2023', 'created_at': '2023-01-15T10:30:00Z'},
                ],
            },
            response_only=True,
        ),
    ],
)
class StatisticsView(generics.GenericAPIView):
    """View for getting overall statistics"""
    serializer_class = StatisticsSerializer
    
    def get(self, request, format=None):
        # Basic counts
        total_records = KilimoSTATData.objects.filter(is_active=True).count()
        total_providers = DataProvider.objects.filter(is_active=True).count()
        total_indicators = Indicator.objects.filter(is_active=True).count()
        total_areas = Area.objects.filter(is_active=True).count()
        
        # Date range
        date_range = KilimoSTATData.objects.filter(is_active=True).aggregate(
            min_year=Min('time_period'),
            max_year=Max('time_period')
        )
        
        # Top sectors by data count
        top_sectors = Sector.objects.filter(
            is_active=True,
            data_records__is_active=True
        ).annotate(
            record_count=Count('data_records')
        ).values('name', 'record_count').order_by('-record_count')[:10]
        
        # Quality distribution from metadata - FIXED: use data_record instead of id
        # Since Metadata uses data_record as primary key, we need to count by data_record
        quality_distribution = Metadata.objects.values('quality_category').annotate(
            count=Count('data_record')  # Changed from 'id' to 'data_record'
        ).order_by('quality_category')
        
        # Recent activity
        recent_uploads = KilimoSTATData.objects.filter(
            is_active=True
        ).order_by('-created_at')[:10].values(
            'id', 'indicator__name', 'area__name', 'time_period', 'created_at'
        )
        
        data = {
            'total_records': total_records,
            'total_providers': total_providers,
            'total_indicators': total_indicators,
            'total_areas': total_areas,
            'date_range': {
                'min': date_range['min_year'],
                'max': date_range['max_year']
            },
            'top_sectors': list(top_sectors),
            'quality_distribution': {
                item['quality_category']: item['count']
                for item in quality_distribution
            },
            'recent_uploads': list(recent_uploads)
        }
        
        serializer = self.get_serializer(data)
        return Response(serializer.data)