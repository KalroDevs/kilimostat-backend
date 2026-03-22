from rest_framework import serializers
from core.models import KilimoSTATData
from .base_serializers import DynamicFieldsModelSerializer, AuditSerializerMixin, GeoJSONSerializer
from .lookup_serializers import (
    AreaSerializer, IndicatorSerializer, UnitSerializer,
    SectorSerializer, SourceSerializer, DataProviderSerializer
)

class KilimoSTATDataSerializer(DynamicFieldsModelSerializer, AuditSerializerMixin):
    """
    Main serializer for KilimoSTATData
    """
    # Nested serializers for detailed view
    area_detail = AreaSerializer(source='area', read_only=True)
    indicator_detail = IndicatorSerializer(source='indicator', read_only=True)
    unit_detail = UnitSerializer(source='unit', read_only=True)
    sector_detail = SectorSerializer(source='sector', read_only=True)
    source_detail = SourceSerializer(source='source', read_only=True)
    provider_detail = DataProviderSerializer(source='provider', read_only=True)
    
    # Display fields
    area_name = serializers.CharField(source='area.name', read_only=True)
    indicator_name = serializers.CharField(source='indicator.name', read_only=True)
    unit_name = serializers.CharField(source='unit.name', read_only=True)
    sector_name = serializers.CharField(source='sector.name', read_only=True)
    source_name = serializers.CharField(source='source.name', read_only=True)
    provider_name = serializers.CharField(source='provider.name', read_only=True)
    
    flag_display = serializers.CharField(source='get_flag_display', read_only=True)
    
    # Computed fields
    value_with_unit = serializers.SerializerMethodField()
    metadata_url = serializers.HyperlinkedRelatedField(
        view_name='metadata-detail',
        read_only=True,
        source='metadata'
    )
    
    class Meta:
        model = KilimoSTATData
        fields = [
            'id', 'slug', 'url',
            # Foreign keys
            'area', 'area_name', 'area_detail',
            'source', 'source_name', 'source_detail',
            'provider', 'provider_name', 'provider_detail',
            'sector', 'sector_name', 'sector_detail',
            'subsector',
            'indicator', 'indicator_name', 'indicator_detail',
            'item', 'domain', 'unit', 'unit_name', 'unit_detail',
            'subgroup_dimension', 'subgroup',
            # Data fields
            'time_period', 'data_value', 'flag', 'flag_display',
            # Quality metrics
            'confidence_lower', 'confidence_upper', 'standard_error', 'sample_size',
            # Computed fields
            'value_with_unit', 'metadata_url',
            # Metadata
            'notes', 'is_active',
            'created_at', 'updated_at', 'created_by'
        ]
        read_only_fields = ['slug', 'created_at', 'updated_at']
    
    def get_value_with_unit(self, obj):
        """Return value with unit symbol"""
        if obj.unit and obj.unit.symbol:
            return f"{obj.data_value} {obj.unit.symbol}"
        return str(obj.data_value)
    
    def validate(self, data):
        """
        Custom validation
        """
        # Ensure confidence_lower <= confidence_upper if both provided
        if data.get('confidence_lower') and data.get('confidence_upper'):
            if data['confidence_lower'] > data['confidence_upper']:
                raise serializers.ValidationError(
                    "confidence_lower must be less than or equal to confidence_upper"
                )
        return data


class KilimoSTATDataListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for list views
    """
    area_name = serializers.CharField(source='area.name')
    indicator_name = serializers.CharField(source='indicator.name')
    unit_symbol = serializers.CharField(source='unit.symbol')
    
    class Meta:
        model = KilimoSTATData
        fields = [
            'id', 'slug', 'area_name', 'indicator_name',
            'time_period', 'data_value', 'unit_symbol', 'flag'
        ]


class KilimoSTATDataGeoSerializer(GeoJSONSerializer):
    """
    GeoJSON serializer for map visualizations
    """
    class Meta:
        model = KilimoSTATData


class DataSummarySerializer(serializers.Serializer):
    """
    Serializer for data summary statistics
    """
    total_records = serializers.IntegerField()
    total_areas = serializers.IntegerField()
    total_indicators = serializers.IntegerField()
    years_covered = serializers.ListField(child=serializers.CharField())
    records_by_sector = serializers.ListField(child=serializers.DictField())
    records_by_year = serializers.ListField(child=serializers.DictField())
    latest_update = serializers.DateTimeField()


class TimeSeriesSerializer(serializers.Serializer):
    """
    Serializer for time series data
    """
    indicator = serializers.CharField()
    area = serializers.CharField()
    data = serializers.ListField(child=serializers.DictField())