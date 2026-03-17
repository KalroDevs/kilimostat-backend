import django_filters
from django.db import models
from django_filters import DateFilter, DateTimeFilter, NumberFilter, CharFilter, BooleanFilter, ChoiceFilter, MultipleChoiceFilter

from core.models import (
    Area, DataProvider, ProviderContact, ProviderDataset, Source,
    Sector, Subsector, Indicator, Item, Unit, Subgroup, SubgroupDimension,
    Domain, KilimoSTATData, IndicatorMetadata, Metadata, MetadataChangeLog,
    Frequency, License
)


# ============================================================================
# AREA FILTERS
# ============================================================================

class AreaFilter(django_filters.FilterSet):
    """Filter for Area model"""
    name = CharFilter(lookup_expr='icontains')
    level = CharFilter(field_name='administrative_level', lookup_expr='exact')
    code = CharFilter(lookup_expr='icontains')
    parent_id = NumberFilter(field_name='parent__id')
    is_active = BooleanFilter()
    created_after = DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = DateTimeFilter(field_name='created_at', lookup_expr='lte')
    
    class Meta:
        model = Area
        fields = ['name', 'level', 'code', 'parent_id', 'is_active']


# ============================================================================
# DATA PROVIDER FILTERS
# ============================================================================

class DataProviderFilter(django_filters.FilterSet):
    """Filter for DataProvider model"""
    name = CharFilter(lookup_expr='icontains')
    abbreviation = CharFilter(lookup_expr='icontains')
    provider_type = MultipleChoiceFilter(choices=DataProvider.PROVIDER_TYPE_CHOICES)
    data_access_policy = ChoiceFilter(choices=DataProvider.DATA_ACCESS_POLICY_CHOICES)
    has_quality_certification = BooleanFilter()
    is_active = BooleanFilter()
    year_established_min = NumberFilter(field_name='year_established', lookup_expr='gte')
    year_established_max = NumberFilter(field_name='year_established', lookup_expr='lte')
    created_after = DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = DateTimeFilter(field_name='created_at', lookup_expr='lte')
    
    class Meta:
        model = DataProvider
        fields = [
            'name', 'abbreviation', 'provider_type', 'data_access_policy',
            'has_quality_certification', 'is_active', 'year_established'
        ]


class ProviderContactFilter(django_filters.FilterSet):
    """Filter for ProviderContact model"""
    provider_id = NumberFilter(field_name='provider__id')
    provider_name = CharFilter(field_name='provider__name', lookup_expr='icontains')
    name = CharFilter(lookup_expr='icontains')
    email = CharFilter(lookup_expr='icontains')
    position = CharFilter(lookup_expr='icontains')
    is_primary = BooleanFilter()
    created_after = DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = DateTimeFilter(field_name='created_at', lookup_expr='lte')
    
    class Meta:
        model = ProviderContact
        fields = ['provider_id', 'provider_name', 'name', 'email', 'position', 'is_primary']


class ProviderDatasetFilter(django_filters.FilterSet):
    """Filter for ProviderDataset model"""
    provider_id = NumberFilter(field_name='provider__id')
    provider_name = CharFilter(field_name='provider__name', lookup_expr='icontains')
    name = CharFilter(lookup_expr='icontains')
    version = CharFilter(lookup_expr='icontains')
    release_date_after = DateFilter(field_name='release_date', lookup_expr='gte')
    release_date_before = DateFilter(field_name='release_date', lookup_expr='lte')
    last_update_after = DateFilter(field_name='last_update', lookup_expr='gte')
    last_update_before = DateFilter(field_name='last_update', lookup_expr='lte')
    is_active = BooleanFilter()
    created_after = DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = DateTimeFilter(field_name='created_at', lookup_expr='lte')
    
    class Meta:
        model = ProviderDataset
        fields = ['provider_id', 'provider_name', 'name', 'version', 'release_date', 'is_active']


# ============================================================================
# SOURCE FILTERS
# ============================================================================

class SourceFilter(django_filters.FilterSet):
    """Filter for Source model"""
    provider_id = NumberFilter(field_name='provider__id')
    provider_name = CharFilter(field_name='provider__name', lookup_expr='icontains')
    name = CharFilter(lookup_expr='icontains')
    code = CharFilter(lookup_expr='icontains')
    source_type = MultipleChoiceFilter(choices=Source.SOURCE_TYPE_CHOICES)
    publication_year = NumberFilter()
    publication_year_min = NumberFilter(field_name='publication_year', lookup_expr='gte')
    publication_year_max = NumberFilter(field_name='publication_year', lookup_expr='lte')
    is_public = BooleanFilter()
    is_active = BooleanFilter()
    created_after = DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = DateTimeFilter(field_name='created_at', lookup_expr='lte')
    
    class Meta:
        model = Source
        fields = [
            'provider_id', 'provider_name', 'name', 'code', 'source_type',
            'publication_year', 'is_public', 'is_active'
        ]


# ============================================================================
# SECTOR/SUBSECTOR FILTERS
# ============================================================================

class SectorFilter(django_filters.FilterSet):
    """Filter for Sector model"""
    name = CharFilter(lookup_expr='icontains')
    code = CharFilter(lookup_expr='icontains')
    description = CharFilter(lookup_expr='icontains')
    is_active = BooleanFilter()
    created_after = DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = DateTimeFilter(field_name='created_at', lookup_expr='lte')
    
    class Meta:
        model = Sector
        fields = ['name', 'code', 'description', 'is_active']


class SubsectorFilter(django_filters.FilterSet):
    """Filter for Subsector model"""
    sector_id = NumberFilter(field_name='sector__id')
    sector_name = CharFilter(field_name='sector__name', lookup_expr='icontains')
    name = CharFilter(lookup_expr='icontains')
    code = CharFilter(lookup_expr='icontains')
    description = CharFilter(lookup_expr='icontains')
    is_active = BooleanFilter()
    created_after = DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = DateTimeFilter(field_name='created_at', lookup_expr='lte')
    
    class Meta:
        model = Subsector
        fields = ['sector_id', 'sector_name', 'name', 'code', 'description', 'is_active']


# ============================================================================
# DOMAIN FILTER
# ============================================================================

class DomainFilter(django_filters.FilterSet):
    """Filter for Domain model"""
    name = CharFilter(lookup_expr='icontains')
    code = CharFilter(lookup_expr='icontains')
    description = CharFilter(lookup_expr='icontains')
    
    class Meta:
        model = Domain
        fields = ['name', 'code', 'description']


# ============================================================================
# UNIT FILTERS
# ============================================================================

class UnitFilter(django_filters.FilterSet):
    """Filter for Unit model"""
    name = CharFilter(lookup_expr='icontains')
    symbol = CharFilter(lookup_expr='icontains')
    category = ChoiceFilter(choices=Unit.UNIT_CATEGORY_CHOICES)
    description = CharFilter(lookup_expr='icontains')
    created_after = DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = DateTimeFilter(field_name='created_at', lookup_expr='lte')
    
    class Meta:
        model = Unit
        fields = ['name', 'symbol', 'category', 'description']


# ============================================================================
# SUBGROUP DIMENSION AND SUBGROUP FILTERS
# ============================================================================

class SubgroupDimensionFilter(django_filters.FilterSet):
    """Filter for SubgroupDimension model"""
    name = CharFilter(lookup_expr='icontains')
    code = CharFilter(lookup_expr='icontains')
    description = CharFilter(lookup_expr='icontains')
    
    class Meta:
        model = SubgroupDimension
        fields = ['name', 'code', 'description']


class SubgroupFilter(django_filters.FilterSet):
    """Filter for Subgroup model"""
    dimension_id = NumberFilter(field_name='dimension__id')
    dimension_name = CharFilter(field_name='dimension__name', lookup_expr='icontains')
    name = CharFilter(lookup_expr='icontains')
    code = CharFilter(lookup_expr='icontains')
    description = CharFilter(lookup_expr='icontains')
    created_after = DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = DateTimeFilter(field_name='created_at', lookup_expr='lte')
    
    class Meta:
        model = Subgroup
        fields = ['dimension_id', 'dimension_name', 'name', 'code', 'description']


# ============================================================================
# INDICATOR FILTERS (UPDATED WITH CORRECT FIELD NAMES)
# ============================================================================

class IndicatorFilter(django_filters.FilterSet):
    """Filter for Indicator model with all relationships"""
    # Basic fields
    name = CharFilter(lookup_expr='icontains')
    code = CharFilter(lookup_expr='icontains')
    description = CharFilter(lookup_expr='icontains')
    is_core_indicator = BooleanFilter()
    is_active = BooleanFilter()
    
    # Domain relationships
    domain_id = NumberFilter(field_name='domain__id')
    domain_name = CharFilter(field_name='domain__name', lookup_expr='icontains')
    domain_code = CharFilter(field_name='domain__code', lookup_expr='icontains')
    
    # Subsector relationships
    subsector_id = NumberFilter(field_name='subsector__id')
    subsector_name = CharFilter(field_name='subsector__name', lookup_expr='icontains')
    subsector_code = CharFilter(field_name='subsector__code', lookup_expr='icontains')
    sector_id = NumberFilter(field_name='subsector__sector__id')
    sector_name = CharFilter(field_name='subsector__sector__name', lookup_expr='icontains')
    
    # Subgroup relationships
    subgroup_id = NumberFilter(field_name='subgroup__id')
    subgroup_name = CharFilter(field_name='subgroup__name', lookup_expr='icontains')
    subgroup_code = CharFilter(field_name='subgroup__code', lookup_expr='icontains')
    subgroup_dimension_id = NumberFilter(field_name='subgroup__dimension__id')
    subgroup_dimension_name = CharFilter(field_name='subgroup__dimension__name', lookup_expr='icontains')
    
    # Unit relationships (UPDATED: changed from unit_of_measure to unit)
    unit_id = NumberFilter(field_name='unit__id')
    unit_name = CharFilter(field_name='unit__name', lookup_expr='icontains')
    unit_symbol = CharFilter(field_name='unit__symbol', lookup_expr='icontains')
    unit_category = ChoiceFilter(field_name='unit__category', choices=Unit.UNIT_CATEGORY_CHOICES)
    
    # Date filters
    created_after = DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = DateTimeFilter(field_name='created_at', lookup_expr='lte')
    updated_after = DateTimeFilter(field_name='updated_at', lookup_expr='gte')
    updated_before = DateTimeFilter(field_name='updated_at', lookup_expr='lte')
    
    class Meta:
        model = Indicator
        fields = [
            'name', 'code', 'is_core_indicator', 'is_active',
            'domain_id', 'subsector_id', 'subgroup_id', 'unit_id'
        ]


# ============================================================================
# ITEM FILTERS
# ============================================================================

class ItemFilter(django_filters.FilterSet):
    """Filter for Item model"""
    category_id = NumberFilter(field_name='category__id')
    category_name = CharFilter(field_name='category__name', lookup_expr='icontains')
    name = CharFilter(lookup_expr='icontains')
    code = CharFilter(lookup_expr='icontains')
    description = CharFilter(lookup_expr='icontains')
    is_active = BooleanFilter()
    created_after = DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = DateTimeFilter(field_name='created_at', lookup_expr='lte')
    
    class Meta:
        model = Item
        fields = ['category_id', 'category_name', 'name', 'code', 'description', 'is_active']


# ============================================================================
# KILIMOSTAT DATA FILTERS
# ============================================================================

class KilimoSTATDataFilter(django_filters.FilterSet):
    """Filter for KilimoSTATData model"""
    
    # Area filters
    area_id = NumberFilter(field_name='area__id')
    area_name = CharFilter(field_name='area__name', lookup_expr='icontains')
    area_level = CharFilter(field_name='area__administrative_level')
    area_code = CharFilter(field_name='area__code', lookup_expr='icontains')
    
    # Source filters
    source_id = NumberFilter(field_name='source__id')
    source_name = CharFilter(field_name='source__name', lookup_expr='icontains')
    
    # Provider filters
    provider_id = NumberFilter(field_name='provider__id')
    provider_name = CharFilter(field_name='provider__name', lookup_expr='icontains')
    
    # Sector filters
    sector_id = NumberFilter(field_name='sector__id')
    sector_name = CharFilter(field_name='sector__name', lookup_expr='icontains')
    
    # Subsector filters
    subsector_id = NumberFilter(field_name='subsector__id')
    subsector_name = CharFilter(field_name='subsector__name', lookup_expr='icontains')
    
    # Indicator filters (updated to use new relationships)
    indicator_id = NumberFilter(field_name='indicator__id')
    indicator_name = CharFilter(field_name='indicator__name', lookup_expr='icontains')
    indicator_code = CharFilter(field_name='indicator__code', lookup_expr='icontains')
    is_core_indicator = BooleanFilter(field_name='indicator__is_core_indicator')
    
    # Indicator relationship filters
    indicator_domain_id = NumberFilter(field_name='indicator__domain__id')
    indicator_domain_name = CharFilter(field_name='indicator__domain__name', lookup_expr='icontains')
    
    indicator_subsector_id = NumberFilter(field_name='indicator__subsector__id')
    indicator_subsector_name = CharFilter(field_name='indicator__subsector__name', lookup_expr='icontains')
    
    indicator_subgroup_id = NumberFilter(field_name='indicator__subgroup__id')
    indicator_subgroup_name = CharFilter(field_name='indicator__subgroup__name', lookup_expr='icontains')
    
    # Unit relationships (UPDATED: changed from unit_of_measure to unit)
    indicator_unit_id = NumberFilter(field_name='indicator__unit__id')
    indicator_unit_name = CharFilter(field_name='indicator__unit__name', lookup_expr='icontains')
    
    # Item filters
    item_id = NumberFilter(field_name='item__id')
    item_name = CharFilter(field_name='item__name', lookup_expr='icontains')
    
    # Domain filters
    domain_id = NumberFilter(field_name='domain__id')
    domain_name = CharFilter(field_name='domain__name', lookup_expr='icontains')
    
    # Unit filters
    unit_id = NumberFilter(field_name='unit__id')
    unit_name = CharFilter(field_name='unit__name', lookup_expr='icontains')
    unit_category = CharFilter(field_name='unit__category')
    
    # Subgroup dimension filters
    subgroup_dimension_id = NumberFilter(field_name='subgroup_dimension__id')
    subgroup_dimension_name = CharFilter(field_name='subgroup_dimension__name', lookup_expr='icontains')
    
    # Subgroup filters
    subgroup_id = NumberFilter(field_name='subgroup__id')
    subgroup_name = CharFilter(field_name='subgroup__name', lookup_expr='icontains')
    
    # Data filters
    time_period = CharFilter(lookup_expr='exact')
    time_period_min = CharFilter(field_name='time_period', lookup_expr='gte')
    time_period_max = CharFilter(field_name='time_period', lookup_expr='lte')
    
    data_value_min = NumberFilter(field_name='data_value', lookup_expr='gte')
    data_value_max = NumberFilter(field_name='data_value', lookup_expr='lte')
    
    flag = MultipleChoiceFilter(choices=KilimoSTATData.FLAG_CHOICES)
    
    # Confidence intervals
    confidence_lower_min = NumberFilter(field_name='confidence_lower', lookup_expr='gte')
    confidence_lower_max = NumberFilter(field_name='confidence_lower', lookup_expr='lte')
    confidence_upper_min = NumberFilter(field_name='confidence_upper', lookup_expr='gte')
    confidence_upper_max = NumberFilter(field_name='confidence_upper', lookup_expr='lte')
    
    sample_size_min = NumberFilter(field_name='sample_size', lookup_expr='gte')
    sample_size_max = NumberFilter(field_name='sample_size', lookup_expr='lte')
    
    # Metadata filters
    is_active = BooleanFilter()
    created_by = CharFilter(lookup_expr='icontains')
    created_after = DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = DateTimeFilter(field_name='created_at', lookup_expr='lte')
    updated_after = DateTimeFilter(field_name='updated_at', lookup_expr='gte')
    updated_before = DateTimeFilter(field_name='updated_at', lookup_expr='lte')
    
    class Meta:
        model = KilimoSTATData
        fields = [
            'area_id', 'source_id', 'provider_id', 'sector_id',
            'subsector_id', 'indicator_id', 'item_id', 'domain_id',
            'unit_id', 'subgroup_dimension_id', 'subgroup_id',
            'time_period', 'flag', 'is_active'
        ]


# ============================================================================
# INDICATOR METADATA FILTERS
# ============================================================================

class IndicatorMetadataFilter(django_filters.FilterSet):
    """Filter for IndicatorMetadata model"""
    indicator_id = NumberFilter(field_name='indicator__id')
    indicator_name = CharFilter(field_name='indicator__name', lookup_expr='icontains')
    
    sector_id = NumberFilter(field_name='sector__id')
    sector_name = CharFilter(field_name='sector__name', lookup_expr='icontains')
    
    sub_sector_id = NumberFilter(field_name='sub_sector__id')
    sub_sector_name = CharFilter(field_name='sub_sector__name', lookup_expr='icontains')
    
    unit_id = NumberFilter(field_name='unit__id')
    unit_name = CharFilter(field_name='unit__name', lookup_expr='icontains')
    
    provider_id = NumberFilter(field_name='data_provider__id')
    provider_name = CharFilter(field_name='data_provider__name', lookup_expr='icontains')
    
    definition = CharFilter(lookup_expr='icontains')
    relevance = CharFilter(lookup_expr='icontains')
    calculation = CharFilter(lookup_expr='icontains')
    
    is_active = BooleanFilter()
    created_after = DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = DateTimeFilter(field_name='created_at', lookup_expr='lte')
    
    class Meta:
        model = IndicatorMetadata
        fields = [
            'indicator_id', 'sector_id', 'sub_sector_id', 'unit_id',
            'provider_id', 'is_active'
        ]


# ============================================================================
# FREQUENCY FILTERS
# ============================================================================

class FrequencyFilter(django_filters.FilterSet):
    """Filter for Frequency model"""
    name = CharFilter(lookup_expr='icontains')
    code = CharFilter(lookup_expr='icontains')
    description = CharFilter(lookup_expr='icontains')
    
    class Meta:
        model = Frequency
        fields = ['name', 'code', 'description']


# ============================================================================
# LICENSE FILTERS
# ============================================================================

class LicenseFilter(django_filters.FilterSet):
    """Filter for License model"""
    name = CharFilter(lookup_expr='icontains')
    code = ChoiceFilter(choices=License.LICENSE_TYPE_CHOICES)
    description = CharFilter(lookup_expr='icontains')
    
    class Meta:
        model = License
        fields = ['name', 'code', 'description']


# ============================================================================
# METADATA FILTERS
# ============================================================================

class MetadataFilter(django_filters.FilterSet):
    """Filter for Metadata model"""
    data_record_id = NumberFilter(field_name='data_record__id')
    
    indicator_metadata_id = NumberFilter(field_name='indicator_metadata__id')
    
    provenance_level = ChoiceFilter(choices=Metadata.PROVENANCE_LEVEL_CHOICES)
    
    quality_score_min = NumberFilter(field_name='quality_score', lookup_expr='gte')
    quality_score_max = NumberFilter(field_name='quality_score', lookup_expr='lte')
    quality_category = ChoiceFilter(choices=Metadata.QUALITY_SCORE_CATEGORY)
    
    completeness_min = NumberFilter(field_name='completeness', lookup_expr='gte')
    completeness_max = NumberFilter(field_name='completeness', lookup_expr='lte')
    
    accuracy_min = NumberFilter(field_name='accuracy', lookup_expr='gte')
    accuracy_max = NumberFilter(field_name='accuracy', lookup_expr='lte')
    
    methodology_type = ChoiceFilter(choices=Metadata.METHOD_TYPE_CHOICES)
    
    time_type = ChoiceFilter(choices=Metadata.TIME_TYPE_CHOICES)
    
    frequency_id = NumberFilter(field_name='frequency__id')
    frequency_name = CharFilter(field_name='frequency__name', lookup_expr='icontains')
    
    geographic_level = ChoiceFilter(choices=Metadata.GEOGRAPHIC_LEVEL_CHOICES)
    
    access_level = ChoiceFilter(choices=Metadata.ACCESS_LEVEL_CHOICES)
    
    license_id = NumberFilter(field_name='license__id')
    license_name = CharFilter(field_name='license__name', lookup_expr='icontains')
    
    review_status = ChoiceFilter(choices=Metadata.REVIEW_STATUS_CHOICES)
    reviewed_by = CharFilter(lookup_expr='icontains')
    
    version = CharFilter(lookup_expr='exact')
    is_latest_version = BooleanFilter()
    
    data_owner = CharFilter(lookup_expr='icontains')
    contact_email = CharFilter(lookup_expr='icontains')
    
    keywords = CharFilter(lookup_expr='icontains')
    sdg_goals = CharFilter(lookup_expr='icontains')
    is_official_statistic = BooleanFilter()
    
    created_by = CharFilter(lookup_expr='icontains')
    modified_by = CharFilter(lookup_expr='icontains')
    
    published_after = DateTimeFilter(field_name='published_at', lookup_expr='gte')
    published_before = DateTimeFilter(field_name='published_at', lookup_expr='lte')
    
    embargo_after = DateTimeFilter(field_name='embargo_until', lookup_expr='gte')
    embargo_before = DateTimeFilter(field_name='embargo_until', lookup_expr='lte')
    
    created_after = DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = DateTimeFilter(field_name='created_at', lookup_expr='lte')
    
    class Meta:
        model = Metadata
        fields = [
            'data_record_id', 'indicator_metadata_id', 'provenance_level',
            'quality_category', 'methodology_type', 'time_type',
            'frequency_id', 'geographic_level', 'access_level',
            'license_id', 'review_status', 'version', 'is_latest_version',
            'is_official_statistic'
        ]


# ============================================================================
# METADATA CHANGE LOG FILTERS
# ============================================================================

class MetadataChangeLogFilter(django_filters.FilterSet):
    """Filter for MetadataChangeLog model"""
    metadata_id = NumberFilter(field_name='metadata__id')
    metadata_record_identifier = CharFilter(
        field_name='metadata__record_identifier', 
        lookup_expr='icontains'
    )
    
    change_type = MultipleChoiceFilter(choices=MetadataChangeLog.CHANGE_TYPE_CHOICES)
    
    changed_by = CharFilter(lookup_expr='icontains')
    
    field_name = CharFilter(lookup_expr='icontains')
    
    changed_after = DateTimeFilter(field_name='changed_at', lookup_expr='gte')
    changed_before = DateTimeFilter(field_name='changed_at', lookup_expr='lte')
    
    class Meta:
        model = MetadataChangeLog
        fields = ['metadata_id', 'change_type', 'changed_by', 'field_name']