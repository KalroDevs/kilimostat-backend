from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.db.models import Count, Q

from core.models import (
    Frequency, License, IndicatorMetadata, Metadata, MetadataChangeLog
)
from api.serializers import (
    FrequencySerializer, LicenseSerializer, IndicatorMetadataSerializer,
    MetadataSerializer, MetadataChangeLogSerializer
)
from api.filters import (
    IndicatorMetadataFilter, MetadataFilter, MetadataChangeLogFilter
)


# ============================================================================
# FREQUENCY VIEWSET
# ============================================================================

class FrequencyViewSet(viewsets.ModelViewSet):
    """ViewSet for Frequency model"""
    queryset = Frequency.objects.all()
    serializer_class = FrequencySerializer
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['name']
    
    @action(detail=True, methods=['get'])
    def usage(self, request, pk=None):
        """Get usage count of this frequency"""
        frequency = self.get_object()
        count = frequency.metadata_records.count()
        return Response({'usage_count': count})


# ============================================================================
# LICENSE VIEWSET
# ============================================================================

class LicenseViewSet(viewsets.ModelViewSet):
    """ViewSet for License model"""
    queryset = License.objects.all()
    serializer_class = LicenseSerializer
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['name']
    
    @action(detail=True, methods=['get'])
    def usage(self, request, pk=None):
        """Get usage count of this license"""
        license = self.get_object()
        count = license.metadata_records.count()
        return Response({'usage_count': count})


# ============================================================================
# INDICATOR METADATA VIEWSET
# ============================================================================

class IndicatorMetadataViewSet(viewsets.ModelViewSet):
    """ViewSet for IndicatorMetadata model"""
    queryset = IndicatorMetadata.objects.all().select_related(
        'indicator', 'sector', 'sub_sector', 'unit', 'data_provider'
    )
    serializer_class = IndicatorMetadataSerializer
    filterset_class = IndicatorMetadataFilter
    search_fields = ['definition', 'relevance', 'calculation']
    ordering_fields = ['created_at', 'updated_at']


# ============================================================================
# METADATA VIEWSET
# ============================================================================

class MetadataViewSet(viewsets.ModelViewSet):
    """ViewSet for Metadata model"""
    queryset = Metadata.objects.all().select_related(
        'data_record', 'indicator_metadata', 'frequency', 'license'
    ).prefetch_related('derived_from', 'change_logs')
    serializer_class = MetadataSerializer
    filterset_class = MetadataFilter
    search_fields = ['record_identifier', 'keywords', 'sdg_goals']
    ordering_fields = ['quality_score', 'version', 'created_at', 'published_at']
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve metadata"""
        metadata = self.get_object()
        metadata.review_status = 'approved'
        metadata.reviewed_by = request.user.username
        metadata.review_date = timezone.now().date()
        metadata.save()
        
        # Create change log
        MetadataChangeLog.objects.create(
            metadata=metadata,
            changed_by=request.user.username,
            change_type='review',
            field_name='review_status',
            old_value=metadata.review_status,
            new_value='approved',
            change_reason=request.data.get('reason', 'Approved via API')
        )
        
        return Response({'status': 'approved', 'message': 'Metadata approved successfully'})
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject metadata"""
        metadata = self.get_object()
        old_status = metadata.review_status
        metadata.review_status = 'rejected'
        metadata.reviewed_by = request.user.username
        metadata.review_date = timezone.now().date()
        metadata.save()
        
        reason = request.data.get('reason', 'Rejected via API')
        
        # Create change log
        MetadataChangeLog.objects.create(
            metadata=metadata,
            changed_by=request.user.username,
            change_type='review',
            field_name='review_status',
            old_value=old_status,
            new_value='rejected',
            change_reason=reason
        )
        
        return Response({
            'status': 'rejected', 
            'message': 'Metadata rejected',
            'reason': reason
        })
    
    @action(detail=True, methods=['get'])
    def history(self, request, pk=None):
        """Get change history for metadata"""
        metadata = self.get_object()
        logs = metadata.change_logs.all()
        serializer = MetadataChangeLogSerializer(logs, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def new_version(self, request, pk=None):
        """Create a new version of metadata"""
        metadata = self.get_object()
        
        # Set current version as not latest
        metadata.is_latest_version = False
        metadata.save()
        
        # Create new version
        metadata.pk = None  # This creates a new instance
        metadata.version = str(float(metadata.version) + 0.1)
        metadata.is_latest_version = True
        metadata.previous_version = metadata
        metadata.save()
        
        serializer = self.get_serializer(metadata)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# ============================================================================
# METADATA CHANGE LOG VIEWSET
# ============================================================================

class MetadataChangeLogViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for MetadataChangeLog model (read-only)"""
    queryset = MetadataChangeLog.objects.all().select_related('metadata').order_by('-changed_at')
    serializer_class = MetadataChangeLogSerializer
    filterset_class = MetadataChangeLogFilter
    search_fields = ['changed_by', 'field_name']
    ordering_fields = ['changed_at', 'change_type']
    
    def get_queryset(self):
        """Filter by metadata_id if provided"""
        queryset = super().get_queryset()
        metadata_id = self.request.query_params.get('metadata_id')
        if metadata_id:
            queryset = queryset.filter(metadata_id=metadata_id)
        return queryset