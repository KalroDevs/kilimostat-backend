from rest_framework import serializers
from core.models import Metadata, IndicatorMetadata, MetadataChangeLog
from .base_serializers import DynamicFieldsModelSerializer, AuditSerializerMixin

class IndicatorMetadataSerializer(DynamicFieldsModelSerializer, AuditSerializerMixin):
    """
    Serializer for IndicatorMetadata
    """
    indicator_name = serializers.CharField(source='indicator.name', read_only=True)
    sector_name = serializers.CharField(source='sector.name', read_only=True)
    sub_sector_name = serializers.CharField(source='sub_sector.name', read_only=True)
    unit_name = serializers.CharField(source='unit.name', read_only=True)
    provider_name = serializers.CharField(source='data_provider.name', read_only=True)
    
    class Meta:
        model = IndicatorMetadata
        fields = [
            'id', 'slug', 'indicator', 'indicator_name',
            'sector', 'sector_name', 'sub_sector', 'sub_sector_name',
            'unit', 'unit_name', 'definition', 'relevance',
            'calculation', 'treatment_of_missing_values', 'disaggregation',
            'source_hyperlink', 'source_description', 'data_provider', 'provider_name',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['slug', 'created_at', 'updated_at']


class MetadataSerializer(DynamicFieldsModelSerializer):
    """
    Serializer for Metadata model
    """
    # Related fields
    data_record_slug = serializers.CharField(source='data_record.slug', read_only=True)
    indicator_metadata_summary = serializers.SerializerMethodField()
    
    # Display fields
    quality_category_display = serializers.CharField(
        source='get_quality_category_display', 
        read_only=True
    )
    provenance_level_display = serializers.CharField(
        source='get_provenance_level_display', 
        read_only=True
    )
    review_status_display = serializers.CharField(
        source='get_review_status_display', 
        read_only=True
    )
    access_level_display = serializers.CharField(
        source='get_access_level_display', 
        read_only=True
    )
    
    class Meta:
        model = Metadata
        fields = [
            'data_record', 'data_record_slug',
            'metadata_version', 'uuid', 'record_identifier',
            'created_at', 'updated_at', 'published_at', 'embargo_until',
            'indicator_metadata', 'indicator_metadata_summary',
            'provenance_level', 'provenance_level_display',
            'original_source_name', 'original_source_url', 'original_source_id',
            'original_data_location', 'processing_notes',
            'quality_score', 'quality_category', 'quality_category_display',
            'completeness', 'accuracy', 'consistency',
            'quality_notes', 'quality_check_date',
            'methodology_type', 'methodology_description', 'methodology_url',
            'sample_size', 'sampling_error', 'response_rate',
            'mean', 'median', 'standard_deviation',
            'range_min', 'range_max',
            'confidence_level', 'confidence_interval_lower', 'confidence_interval_upper',
            'time_type', 'reference_period_start', 'reference_period_end',
            'reference_period_description', 'frequency',
            'geographic_level', 'geographic_scope', 'spatial_resolution',
            'access_level', 'access_level_display',
            'license_type', 'license_url', 'citation_recommendation',
            'download_count', 'view_count', 'last_accessed',
            'review_status', 'review_status_display',
            'review_date', 'reviewed_by', 'reviewer_notes',
            'approved_by', 'approval_date',
            'version', 'version_notes', 'is_latest_version',
            'data_owner', 'contact_email',
            'keywords', 'sdg_goals', 'is_official_statistic',
            'custom_metadata', 'created_by', 'modified_by'
        ]
        read_only_fields = ['uuid', 'created_at', 'updated_at', 'download_count', 'view_count']
    
    def get_indicator_metadata_summary(self, obj):
        """Get summary of linked indicator metadata"""
        if obj.indicator_metadata:
            return {
                'definition': obj.indicator_metadata.definition[:100] + '...' if obj.indicator_metadata.definition else None,
                'has_calculation': bool(obj.indicator_metadata.calculation)
            }
        return None


class MetadataChangeLogSerializer(serializers.ModelSerializer):
    """
    Serializer for MetadataChangeLog
    """
    change_type_display = serializers.CharField(source='get_change_type_display', read_only=True)
    
    class Meta:
        model = MetadataChangeLog
        fields = [
            'id', 'metadata', 'changed_at', 'changed_by',
            'change_type', 'change_type_display',
            'field_name', 'old_value', 'new_value', 'change_reason'
        ]
        read_only_fields = ['changed_at']