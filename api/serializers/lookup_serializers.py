from rest_framework import serializers
from core.models import *
from .base_serializers import DynamicFieldsModelSerializer, AuditSerializerMixin

class AreaSerializer(DynamicFieldsModelSerializer, AuditSerializerMixin):
    """
    Serializer for Area model
    """
    parent_name = serializers.CharField(source='parent.name', read_only=True)
    children_count = serializers.IntegerField(source='children.count', read_only=True)
    level_display = serializers.CharField(source='get_level_display', read_only=True)
    
    class Meta:
        model = Area
        fields = [
            'id', 'name', 'level', 'level_display', 'code', 
            'parent', 'parent_name', 'children_count',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class DataProviderSerializer(DynamicFieldsModelSerializer, AuditSerializerMixin):
    """
    Serializer for DataProvider model
    """
    provider_type_display = serializers.CharField(source='get_provider_type_display', read_only=True)
    sources_count = serializers.IntegerField(source='sources.count', read_only=True)
    indicators_count = serializers.IntegerField(source='indicators.count', read_only=True)
    
    class Meta:
        model = DataProvider
        fields = [
            'id', 'name', 'code', 'provider_type', 'provider_type_display',
            'contact_person', 'email', 'phone', 'website', 'description',
            'sources_count', 'indicators_count', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class SourceSerializer(DynamicFieldsModelSerializer, AuditSerializerMixin):
    """
    Serializer for Source model
    """
    source_type_display = serializers.CharField(source='get_source_type_display', read_only=True)
    provider_name = serializers.CharField(source='provider.name', read_only=True)
    
    class Meta:
        model = Source
        fields = [
            'id', 'name', 'code', 'provider', 'provider_name',
            'source_type', 'source_type_display', 'publication_year',
            'access_url', 'is_public', 'description', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class SectorSerializer(DynamicFieldsModelSerializer):
    """
    Serializer for Sector model
    """
    sector_display = serializers.CharField(source='get_code_display', read_only=True)
    subsectors_count = serializers.IntegerField(source='subsectors.count', read_only=True)
    
    class Meta:
        model = Sector
        fields = [
            'id', 'name', 'code', 'sector_display', 'description',
            'display_order', 'subsectors_count', 'is_active'
        ]


class SubsectorSerializer(DynamicFieldsModelSerializer):
    """
    Serializer for Subsector model
    """
    sector_name = serializers.CharField(source='sector.name', read_only=True)
    
    class Meta:
        model = Subsector
        fields = [
            'id', 'sector', 'sector_name', 'name', 'description',
            'display_order', 'is_active'
        ]


class IndicatorSerializer(DynamicFieldsModelSerializer, AuditSerializerMixin):
    """
    Serializer for Indicator model
    """
    metadata_summary = serializers.SerializerMethodField()
    
    class Meta:
        model = Indicator
        fields = [
            'id', 'name', 'code', 'description', 'unit_of_measure',
            'is_core_indicator', 'is_active', 'metadata_summary',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_metadata_summary(self, obj):
        """Get summary of indicator metadata"""
        try:
            metadata = obj.metadata
            return {
                'definition': metadata.definition[:200] + '...' if len(metadata.definition) > 200 else metadata.definition,
                'has_calculation': bool(metadata.calculation),
                'data_provider': metadata.data_provider.name if metadata.data_provider else None
            }
        except:
            return None


class ItemSerializer(DynamicFieldsModelSerializer):
    """
    Serializer for Item model
    """
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    
    class Meta:
        model = Item
        fields = [
            'id', 'name', 'category', 'category_display',
            'description', 'is_active'
        ]


class DomainSerializer(DynamicFieldsModelSerializer):
    """
    Serializer for Domain model
    """
    domain_display = serializers.CharField(source='get_code_display', read_only=True)
    
    class Meta:
        model = Domain
        fields = ['id', 'name', 'code', 'domain_display', 'description']


class UnitSerializer(DynamicFieldsModelSerializer):
    """
    Serializer for Unit model
    """
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    
    class Meta:
        model = Unit
        fields = [
            'id', 'name', 'symbol', 'category', 'category_display', 'description'
        ]


class SubgroupDimensionSerializer(DynamicFieldsModelSerializer):
    """
    Serializer for SubgroupDimension model
    """
    dimension_display = serializers.CharField(source='get_code_display', read_only=True)
    subgroups_count = serializers.IntegerField(source='subgroups.count', read_only=True)
    
    class Meta:
        model = SubgroupDimension
        fields = [
            'id', 'name', 'code', 'dimension_display',
            'description', 'subgroups_count'
        ]


class SubgroupSerializer(DynamicFieldsModelSerializer):
    """
    Serializer for Subgroup model
    """
    dimension_name = serializers.CharField(source='dimension.name', read_only=True)
    
    class Meta:
        model = Subgroup
        fields = [
            'id', 'dimension', 'dimension_name', 'name', 'description'
        ]