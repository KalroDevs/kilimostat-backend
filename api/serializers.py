from rest_framework import serializers
from django.utils.text import slugify

# Import models directly from core app
from core.models import (
    Area, DataProvider, Source, Sector, Subsector, Indicator,
    ItemCategory, Item, Domain, Unit, SubgroupDimension, Subgroup,
    ProviderContact, ProviderDataset, KilimoSTATData, IndicatorMetadata,
    Frequency, License, Metadata, MetadataChangeLog
)


# ============================================================================
# BASE SERIALIZERS
# ============================================================================

class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    """
    A ModelSerializer that takes an additional `fields` argument that
    controls which fields should be displayed.
    """
    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)
        super().__init__(*args, **kwargs)

        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)


# ============================================================================
# AREA SERIALIZERS
# ============================================================================

class AreaSerializer(DynamicFieldsModelSerializer):
    """Serializer for Area model"""
    full_hierarchy = serializers.SerializerMethodField()
    children_count = serializers.IntegerField(source='get_children_count', read_only=True)
    
    class Meta:
        model = Area
        fields = [
            'id', 'name', 'administrative_level', 'code', 'parent',
            'latitude', 'longitude', 'is_active', 'full_hierarchy',
            'children_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_full_hierarchy(self, obj):
        """Get full hierarchy path"""
        return ' > '.join([a.name for a in obj.get_ancestors()] + [obj.name])


class AreaDetailSerializer(AreaSerializer):
    """Detailed Area serializer with children"""
    children = AreaSerializer(many=True, read_only=True, source='get_children')
    
    class Meta(AreaSerializer.Meta):
        fields = AreaSerializer.Meta.fields + ['children']


# ============================================================================
# DATA PROVIDER SERIALIZERS
# ============================================================================

class ProviderContactSerializer(serializers.ModelSerializer):
    """Serializer for ProviderContact"""
    class Meta:
        model = ProviderContact
        fields = [
            'id', 'name', 'position', 'email', 'phone',
            'is_primary', 'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class ProviderDatasetSerializer(serializers.ModelSerializer):
    """Serializer for ProviderDataset"""
    class Meta:
        model = ProviderDataset
        fields = [
            'id', 'name', 'description', 'release_date', 'last_update',
            'version', 'methodology', 'geographic_coverage', 'temporal_coverage',
            'url', 'citation', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class DataProviderSerializer(DynamicFieldsModelSerializer):
    """Serializer for DataProvider"""
    contact_count = serializers.IntegerField(read_only=True)
    dataset_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = DataProvider
        fields = [
            'id', 'name', 'abbreviation', 'provider_type', 'contact_person',
            'email', 'phone', 'website', 'physical_address', 'headquarters_location',
            'year_established', 'mandate', 'description', 'data_collection_methods',
            'sampling_framework', 'data_frequency', 'has_quality_certification',
            'quality_certification_details', 'qa_procedures', 'collaborating_institutions',
            'funding_sources', 'data_access_policy', 'data_license', 'citation_recommendation',
            'logo', 'notes', 'is_active', 'contact_count', 'dataset_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class DataProviderDetailSerializer(DataProviderSerializer):
    """Detailed DataProvider serializer with contacts and datasets"""
    contacts = ProviderContactSerializer(many=True, read_only=True)
    datasets = ProviderDatasetSerializer(many=True, read_only=True)
    
    class Meta(DataProviderSerializer.Meta):
        fields = DataProviderSerializer.Meta.fields + ['contacts', 'datasets']


# ============================================================================
# SOURCE SERIALIZERS
# ============================================================================

class SourceSerializer(DynamicFieldsModelSerializer):
    """Serializer for Source"""
    provider_name = serializers.CharField(source='provider.name', read_only=True)
    
    class Meta:
        model = Source
        fields = [
            'id', 'name', 'code', 'provider', 'provider_name',
            'source_type', 'publication_year', 'access_url',
            'is_public', 'description', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


# ============================================================================
# SECTOR/SUBSECTOR SERIALIZERS
# ============================================================================

class SubsectorSerializer(DynamicFieldsModelSerializer):
    """Serializer for Subsector"""
    sector_name = serializers.CharField(source='sector.name', read_only=True)
    
    class Meta:
        model = Subsector
        fields = [
            'id', 'sector', 'sector_name', 'name', 'code',
            'description', 'display_order', 'is_active'
        ]


class SectorSerializer(DynamicFieldsModelSerializer):
    """Serializer for Sector"""
    subsector_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Sector
        fields = [
            'id', 'name', 'code', 'description',
            'display_order', 'is_active', 'subsector_count'
        ]


class SectorDetailSerializer(SectorSerializer):
    """Detailed Sector serializer with subsectors"""
    subsectors = SubsectorSerializer(many=True, read_only=True)
    
    class Meta(SectorSerializer.Meta):
        fields = SectorSerializer.Meta.fields + ['subsectors']


# ============================================================================
# INDICATOR SERIALIZERS
# ============================================================================

class IndicatorSerializer(DynamicFieldsModelSerializer):
    """Serializer for Indicator"""
    data_count = serializers.IntegerField(read_only=True)
    domain_name = serializers.CharField(source='domain.name', read_only=True)
    subsector_name = serializers.CharField(source='subsector.name', read_only=True)
    subgroup_name = serializers.CharField(source='subgroup.name', read_only=True)
    unit_name = serializers.CharField(source='unit.name', read_only=True)
    unit_symbol = serializers.CharField(source='unit.symbol', read_only=True)
    
    class Meta:
        model = Indicator
        fields = [
            'id', 'name', 'code', 'domain', 'domain_name',
            'subsector', 'subsector_name', 'subgroup', 'subgroup_name',
            'unit', 'unit_name', 'unit_symbol', 'description',
            'is_core_indicator', 'is_active', 'data_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


# ============================================================================
# ITEM SERIALIZERS
# ============================================================================

class ItemCategorySerializer(DynamicFieldsModelSerializer):
    """Serializer for ItemCategory"""
    item_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = ItemCategory
        fields = [
            'id', 'name', 'code', 'description',
            'display_order', 'item_count'
        ]


class ItemSerializer(DynamicFieldsModelSerializer):
    """Serializer for Item"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    data_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Item
        fields = [
            'id', 'category', 'category_name', 'name', 'code',
            'description', 'is_active', 'data_count'
        ]


# ============================================================================
# DOMAIN SERIALIZER
# ============================================================================

class DomainSerializer(DynamicFieldsModelSerializer):
    """Serializer for Domain"""
    data_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Domain
        fields = ['id', 'name', 'code', 'description', 'data_count']


# ============================================================================
# UNIT SERIALIZER
# ============================================================================

class UnitSerializer(DynamicFieldsModelSerializer):
    """Serializer for Unit model"""
    data_count = serializers.IntegerField(read_only=True, required=False)
    
    class Meta:
        model = Unit
        fields = [
            'id', 'name', 'symbol', 'category',
            'description', 'data_count'
        ]


# ============================================================================
# SUBGROUP SERIALIZERS
# ============================================================================

class SubgroupSerializer(DynamicFieldsModelSerializer):
    """Serializer for Subgroup"""
    dimension_name = serializers.CharField(source='dimension.name', read_only=True)
    data_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Subgroup
        fields = [
            'id', 'dimension', 'dimension_name', 'name',
            'code', 'description', 'data_count'
        ]


class SubgroupDimensionSerializer(DynamicFieldsModelSerializer):
    """Serializer for SubgroupDimension"""
    subgroup_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = SubgroupDimension
        fields = [
            'id', 'name', 'code', 'description', 'subgroup_count'
        ]


class SubgroupDimensionDetailSerializer(SubgroupDimensionSerializer):
    """Detailed SubgroupDimension serializer with subgroups"""
    subgroups = SubgroupSerializer(many=True, read_only=True)
    
    class Meta(SubgroupDimensionSerializer.Meta):
        fields = SubgroupDimensionSerializer.Meta.fields + ['subgroups']


# ============================================================================
# KILIMOSTAT DATA SERIALIZERS
# ============================================================================

class KilimoSTATDataSerializer(DynamicFieldsModelSerializer):
    """Serializer for KilimoSTATData"""
    # Readable field representations
    area_name = serializers.CharField(source='area.name', read_only=True)
    area_level = serializers.CharField(source='area.administrative_level', read_only=True)
    source_name = serializers.CharField(source='source.name', read_only=True)
    provider_name = serializers.CharField(source='provider.name', read_only=True)
    sector_name = serializers.CharField(source='sector.name', read_only=True)
    subsector_name = serializers.CharField(source='subsector.name', read_only=True)
    indicator_name = serializers.CharField(source='indicator.name', read_only=True)
    item_name = serializers.CharField(source='item.name', read_only=True)
    domain_name = serializers.CharField(source='domain.name', read_only=True)
    unit_name = serializers.CharField(source='unit.name', read_only=True)
    unit_symbol = serializers.CharField(source='unit.symbol', read_only=True)
    subgroup_dimension_name = serializers.CharField(
        source='subgroup_dimension.name', read_only=True
    )
    subgroup_name = serializers.CharField(source='subgroup.name', read_only=True)
    
    # Quality badge from metadata
    quality_badge = serializers.SerializerMethodField()
    
    class Meta:
        model = KilimoSTATData
        fields = [
            'id', 'slug', 'area', 'area_name', 'area_level',
            'source', 'source_name', 'provider', 'provider_name',
            'sector', 'sector_name', 'subsector', 'subsector_name',
            'indicator', 'indicator_name',
            'item', 'item_name', 'domain', 'domain_name',
            'unit', 'unit_name', 'unit_symbol',
            'subgroup_dimension', 'subgroup_dimension_name',
            'subgroup', 'subgroup_name',
            'time_period', 'data_value', 'flag',
            'confidence_lower', 'confidence_upper', 'standard_error',
            'sample_size', 'notes', 'is_active',
            'quality_badge', 'created_at', 'updated_at', 'created_by'
        ]
        read_only_fields = ['slug', 'created_at', 'updated_at']
    
    def get_quality_badge(self, obj):
        """Get quality information from metadata"""
        metadata = obj.get_metadata()
        if metadata and metadata.quality_score:
            return {
                'score': metadata.quality_score,
                'category': metadata.quality_category
            }
        return None
    
    def validate(self, data):
        """Validate subgroup fields"""
        if (data.get('subgroup_dimension') is None) != (data.get('subgroup') is None):
            raise serializers.ValidationError(
                "Both subgroup_dimension and subgroup must be set together or both null"
            )
        return data


class KilimoSTATDataDetailSerializer(KilimoSTATDataSerializer):
    """Detailed KilimoSTATData serializer with metadata"""
    metadata = serializers.SerializerMethodField()
    
    class Meta(KilimoSTATDataSerializer.Meta):
        fields = KilimoSTATDataSerializer.Meta.fields + ['metadata']
    
    def get_metadata(self, obj):
        """Get full metadata if exists"""
        metadata = obj.get_metadata()
        if metadata:
            return MetadataSerializer(metadata).data
        return None


# ============================================================================
# METADATA SERIALIZERS - FIXED
# ============================================================================

class FrequencySerializer(serializers.ModelSerializer):
    """Serializer for Frequency"""
    class Meta:
        model = Frequency
        fields = ['id', 'name', 'code', 'description']


class LicenseSerializer(serializers.ModelSerializer):
    """Serializer for License"""
    class Meta:
        model = License
        fields = ['id', 'name', 'code', 'url', 'description']


class IndicatorMetadataSerializer(serializers.ModelSerializer):
    """Serializer for IndicatorMetadata"""
    indicator_name = serializers.CharField(source='indicator.name', read_only=True)
    sector_name = serializers.CharField(source='sector.name', read_only=True)
    sub_sector_name = serializers.CharField(source='sub_sector.name', read_only=True)
    unit_name = serializers.CharField(source='unit.name', read_only=True)
    unit_symbol = serializers.CharField(source='unit.symbol', read_only=True)
    provider_name = serializers.CharField(source='data_provider.name', read_only=True)
    
    class Meta:
        model = IndicatorMetadata
        fields = [
            'id', 'slug', 'indicator', 'indicator_name',
            'sector', 'sector_name', 'sub_sector', 'sub_sector_name',
            'unit', 'unit_name', 'unit_symbol', 'definition', 'relevance',
            'calculation', 'treatment_of_missing_values', 'disaggregation',
            'source_hyperlink', 'source_description', 'data_provider',
            'provider_name', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['slug', 'created_at', 'updated_at']


class MetadataSerializer(serializers.ModelSerializer):
    """Serializer for Metadata - FIXED: removed 'id' field"""
    # Related field representations
    data_record_info = serializers.SerializerMethodField()
    frequency_name = serializers.CharField(source='frequency.name', read_only=True)
    license_name = serializers.CharField(source='license.name', read_only=True)
    license_code = serializers.CharField(source='license.code', read_only=True)
    
    class Meta:
        model = Metadata
        # Remove 'id' from fields since Metadata uses data_record as PK
        fields = [
            'data_record', 'data_record_info', 'metadata_version',
            'uuid', 'record_identifier', 'indicator_metadata',
            'provenance_level', 'original_source_name', 'original_source_url',
            'original_source_id', 'original_data_location', 'processing_notes',
            'quality_score', 'quality_category', 'completeness', 'accuracy',
            'consistency', 'quality_notes', 'quality_check_date',
            'methodology_type', 'methodology_description', 'methodology_url',
            'sample_size', 'sampling_error', 'response_rate',
            'mean', 'median', 'standard_deviation', 'range_min', 'range_max',
            'confidence_level', 'confidence_interval_lower', 'confidence_interval_upper',
            'time_type', 'reference_period_start', 'reference_period_end',
            'reference_period_description', 'frequency', 'frequency_name',
            'geographic_level', 'geographic_scope', 'spatial_resolution',
            'access_level', 'license', 'license_name', 'license_code',
            'license_url', 'citation_recommendation', 'download_count', 'view_count',
            'last_accessed', 'review_status', 'review_date', 'reviewed_by',
            'reviewer_notes', 'approved_by', 'approval_date', 'version',
            'version_notes', 'is_latest_version', 'data_owner', 'contact_email',
            'keywords', 'sdg_goals', 'is_official_statistic', 'custom_metadata',
            'created_by', 'modified_by', 'created_at', 'updated_at', 'published_at',
            'embargo_until'
        ]
        read_only_fields = ['uuid', 'created_at', 'updated_at']
    
    def get_data_record_info(self, obj):
        """Get basic info about the associated data record"""
        if obj.data_record:
            return {
                'id': obj.data_record.id,
                'slug': obj.data_record.slug,
                'indicator': obj.data_record.indicator.name,
                'area': obj.data_record.area.name,
                'time_period': obj.data_record.time_period,
                'value': obj.data_record.data_value
            }
        return None


class MetadataChangeLogSerializer(serializers.ModelSerializer):
    """Serializer for MetadataChangeLog"""
    metadata_info = serializers.SerializerMethodField()
    
    class Meta:
        model = MetadataChangeLog
        fields = [
            'id', 'metadata', 'metadata_info', 'changed_at',
            'changed_by', 'change_type', 'field_name',
            'old_value', 'new_value', 'change_reason'
        ]
        read_only_fields = ['changed_at']
    
    def get_metadata_info(self, obj):
        """Get basic info about the metadata"""
        if obj.metadata:
            return {
                'data_record': obj.metadata.data_record_id,
                'record_identifier': obj.metadata.record_identifier,
                'version': obj.metadata.version
            }
        return None


# ============================================================================
# STATISTICS SERIALIZER
# ============================================================================

class StatisticsSerializer(serializers.Serializer):
    """Serializer for statistics endpoint"""
    total_records = serializers.IntegerField(required=False, default=0)
    total_providers = serializers.IntegerField(required=False, default=0)
    total_indicators = serializers.IntegerField(required=False, default=0)
    total_areas = serializers.IntegerField(required=False, default=0)
    date_range = serializers.DictField(child=serializers.CharField(), required=False, default=dict)
    top_sectors = serializers.ListField(child=serializers.DictField(), required=False, default=list)
    quality_distribution = serializers.DictField(child=serializers.IntegerField(), required=False, default=dict)
    recent_uploads = serializers.ListField(child=serializers.DictField(), required=False, default=list)