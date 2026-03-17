from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count, Q
from django.utils import timezone
from django.utils.text import slugify
from django import forms
import json

from import_export.admin import ImportExportModelAdmin
from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget, FloatWidget, IntegerWidget
from import_export.tmp_storages import TempFolderStorage

from .models import (
    Area, DataProvider, Source, Sector, Subsector, Indicator, 
    ItemCategory, Item, Domain, Unit, SubgroupDimension, Subgroup,
    ProviderContact, ProviderDataset, KilimoSTATData, IndicatorMetadata,
    Frequency, License, Metadata, MetadataChangeLog
)


# ============================================================================
# IMPORT/EXPORT RESOURCES
# ============================================================================

class KilimoSTATDataResource(resources.ModelResource):
    """Resource for importing/exporting KilimoSTATData"""
    
    # Foreign key fields with widgets
    area = fields.Field(
        column_name='area',
        attribute='area',
        widget=ForeignKeyWidget(Area, field='name')
    )
    source = fields.Field(
        column_name='source',
        attribute='source',
        widget=ForeignKeyWidget(Source, field='name')
    )
    provider = fields.Field(
        column_name='provider',
        attribute='provider',
        widget=ForeignKeyWidget(DataProvider, field='name')
    )
    sector = fields.Field(
        column_name='sector',
        attribute='sector',
        widget=ForeignKeyWidget(Sector, field='name')
    )
    subsector = fields.Field(
        column_name='subsector',
        attribute='subsector',
        widget=ForeignKeyWidget(Subsector, field='name')
    )
    indicator = fields.Field(
        column_name='indicator',
        attribute='indicator',
        widget=ForeignKeyWidget(Indicator, field='name')
    )
    item = fields.Field(
        column_name='item',
        attribute='item',
        widget=ForeignKeyWidget(Item, field='name')
    )
    domain = fields.Field(
        column_name='domain',
        attribute='domain',
        widget=ForeignKeyWidget(Domain, field='name')
    )
    unit = fields.Field(
        column_name='unit',
        attribute='unit',
        widget=ForeignKeyWidget(Unit, field='name')
    )
    subgroup_dimension = fields.Field(
        column_name='subgroup_dimension',
        attribute='subgroup_dimension',
        widget=ForeignKeyWidget(SubgroupDimension, field='name')
    )
    subgroup = fields.Field(
        column_name='subgroup',
        attribute='subgroup',
        widget=ForeignKeyWidget(Subgroup, field='name')
    )
    
    # Data fields
    data_value = fields.Field(
        column_name='data_value',
        attribute='data_value',
        widget=FloatWidget()
    )
    confidence_lower = fields.Field(
        column_name='confidence_lower',
        attribute='confidence_lower',
        widget=FloatWidget()
    )
    confidence_upper = fields.Field(
        column_name='confidence_upper',
        attribute='confidence_upper',
        widget=FloatWidget()
    )
    standard_error = fields.Field(
        column_name='standard_error',
        attribute='standard_error',
        widget=FloatWidget()
    )
    sample_size = fields.Field(
        column_name='sample_size',
        attribute='sample_size',
        widget=IntegerWidget()
    )
    
    # Export only fields
    area_code = fields.Field(attribute='area__code', readonly=True)
    area_level = fields.Field(attribute='area__administrative_level', readonly=True)
    indicator_code = fields.Field(attribute='indicator__code', readonly=True)
    unit_symbol = fields.Field(attribute='unit__symbol', readonly=True)
    created_at_formatted = fields.Field(attribute='created_at', readonly=True)
    metadata_quality = fields.Field(readonly=True)
    
    def dehydrate_created_at_formatted(self, obj):
        """Format created_at for export"""
        return obj.created_at.strftime('%Y-%m-%d %H:%M:%S') if obj.created_at else ''
    
    def dehydrate_metadata_quality(self, obj):
        """Get quality score from metadata"""
        metadata = obj.get_metadata()
        return metadata.quality_score if metadata else ''
    
    def before_import_row(self, row, **kwargs):
        """Validate and prepare data before import"""
        # Generate slug if not provided
        if not row.get('slug'):
            area_name = row.get('area', '')
            indicator_name = row.get('indicator', '')
            time_period = row.get('time_period', '')
            item_name = row.get('item', '')
            
            base = f"{area_name}-{indicator_name}-{time_period}"
            if item_name:
                base += f"-{item_name}"
            row['slug'] = slugify(base)[:500]
        
        # Set default values
        if not row.get('is_active'):
            row['is_active'] = '1'
        if not row.get('flag'):
            row['flag'] = ''
        if not row.get('notes'):
            row['notes'] = ''
        if not row.get('created_by'):
            row['created_by'] = 'import'
    
    def skip_row(self, instance, original):
        """Skip duplicate rows based on slug"""
        if original and original.slug == instance.slug:
            return True
        return False
    
    class Meta:
        model = KilimoSTATData
        import_id_fields = ['slug']
        fields = [
            'id', 'slug', 'area', 'source', 'provider', 'sector', 'subsector',
            'indicator', 'item', 'domain', 'unit', 'subgroup_dimension', 'subgroup',
            'time_period', 'data_value', 'flag', 'confidence_lower', 'confidence_upper',
            'standard_error', 'sample_size', 'notes', 'is_active', 'created_by',
            # Export only fields
            'area_code', 'area_level', 'indicator_code',
            'unit_symbol', 'created_at_formatted', 'metadata_quality'
        ]
        export_order = fields
        skip_unchanged = True
        report_skipped = True


# ============================================================================
# CUSTOM FILTERS
# ============================================================================

class YearFilter(SimpleListFilter):
    """Custom filter for year-based filtering"""
    title = 'year'
    parameter_name = 'year'

    def lookups(self, request, model_admin):
        years = []
        if hasattr(model_admin.model, 'publication_year'):
            years = model_admin.model.objects.exclude(
                publication_year__isnull=True
            ).values_list('publication_year', flat=True).distinct().order_by('-publication_year')
        elif hasattr(model_admin.model, 'release_date'):
            years = model_admin.model.objects.exclude(
                release_date__isnull=True
            ).dates('release_date', 'year')
            years = [d.year for d in years]
        
        return [(year, str(year)) for year in years[:10]]

    def queryset(self, request, queryset):
        if self.value():
            if hasattr(queryset.model, 'publication_year'):
                return queryset.filter(publication_year=self.value())
            elif hasattr(queryset.model, 'release_date'):
                return queryset.filter(release_date__year=self.value())
        return queryset


class DataQualityFilter(SimpleListFilter):
    """Filter for data quality categories"""
    title = 'data quality'
    parameter_name = 'quality'

    def lookups(self, request, model_admin):
        return [
            ('excellent', 'Excellent (90-100)'),
            ('good', 'Good (75-89)'),
            ('fair', 'Fair (60-74)'),
            ('poor', 'Poor (0-59)'),
            ('unassessed', 'Not Assessed'),
        ]

    def queryset(self, request, queryset):
        if self.value() == 'excellent':
            return queryset.filter(quality_score__gte=90)
        elif self.value() == 'good':
            return queryset.filter(quality_score__gte=75, quality_score__lt=90)
        elif self.value() == 'fair':
            return queryset.filter(quality_score__gte=60, quality_score__lt=75)
        elif self.value() == 'poor':
            return queryset.filter(quality_score__lt=60)
        elif self.value() == 'unassessed':
            return queryset.filter(quality_score__isnull=True)
        return queryset


class AdministrativeLevelFilter(SimpleListFilter):
    """Filter for Area administrative levels"""
    title = 'administrative level'
    parameter_name = 'level'

    def lookups(self, request, model_admin):
        return Area.LEVEL_CHOICES

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(administrative_level=self.value())
        return queryset


class IndicatorDomainFilter(SimpleListFilter):
    """Filter for indicators by domain"""
    title = 'domain'
    parameter_name = 'domain'

    def lookups(self, request, model_admin):
        domains = Domain.objects.all()
        return [(d.id, d.name) for d in domains]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(domain_id=self.value())
        return queryset


class IndicatorSubsectorFilter(SimpleListFilter):
    """Filter for indicators by subsector"""
    title = 'subsector'
    parameter_name = 'subsector'

    def lookups(self, request, model_admin):
        subsectors = Subsector.objects.filter(is_active=True).select_related('sector')
        return [(s.id, f"{s.sector.name} - {s.name}") for s in subsectors]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(subsector_id=self.value())
        return queryset


class IndicatorSubgroupFilter(SimpleListFilter):
    """Filter for indicators by subgroup"""
    title = 'subgroup'
    parameter_name = 'subgroup'

    def lookups(self, request, model_admin):
        subgroups = Subgroup.objects.all().select_related('dimension')
        return [(s.id, f"{s.dimension.name}: {s.name}") for s in subgroups]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(subgroup_id=self.value())
        return queryset


class IndicatorUnitFilter(SimpleListFilter):
    """Filter for indicators by unit"""
    title = 'unit'
    parameter_name = 'unit'

    def lookups(self, request, model_admin):
        units = Unit.objects.all()
        return [(u.id, f"{u.name} ({u.symbol})" if u.symbol else u.name) for u in units]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(unit_id=self.value())
        return queryset


# ============================================================================
# INLINE ADMIN CLASSES
# ============================================================================

class ProviderContactInline(admin.TabularInline):
    """Inline admin for provider contacts"""
    model = ProviderContact
    extra = 1
    fields = ['name', 'position', 'email', 'phone', 'is_primary']
    readonly_fields = ['created_at', 'updated_at']


class ProviderDatasetInline(admin.TabularInline):
    """Inline admin for provider datasets"""
    model = ProviderDataset
    extra = 0
    fields = ['name', 'release_date', 'version', 'is_active']
    readonly_fields = ['created_at', 'updated_at']
    show_change_link = True


class SubsectorInline(admin.TabularInline):
    """Inline admin for subsectors"""
    model = Subsector
    extra = 1
    fields = ['name', 'code', 'display_order', 'is_active']


class IndicatorInline(admin.TabularInline):
    """Inline admin for indicators within subsector"""
    model = Indicator
    extra = 1
    fields = ['name', 'code', 'domain', 'unit', 'is_core_indicator', 'is_active']
    show_change_link = True


class SubgroupInline(admin.TabularInline):
    """Inline admin for subgroups"""
    model = Subgroup
    extra = 1
    fields = ['name', 'code', 'description']


class ItemInline(admin.TabularInline):
    """Inline admin for items"""
    model = Item
    extra = 1
    fields = ['name', 'code', 'is_active']


class MetadataInline(admin.StackedInline):
    """Inline admin for metadata"""
    model = Metadata
    can_delete = False
    fieldsets = (
        ('Basic Information', {
            'fields': ('metadata_version', 'uuid', 'record_identifier', 
                      'published_at', 'embargo_until')
        }),
        ('Quality Metrics', {
            'fields': ('quality_score', 'quality_category', 'completeness', 
                      'accuracy', 'consistency'),
            'classes': ('collapse',)
        }),
        ('Access Information', {
            'fields': ('access_level', 'license', 'license_url', 
                      'citation_recommendation'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['uuid', 'created_at', 'updated_at']


class MetadataChangeLogInline(admin.TabularInline):
    """Inline admin for metadata change logs"""
    model = MetadataChangeLog
    extra = 0
    fields = ['changed_at', 'changed_by', 'change_type', 'field_name']
    readonly_fields = ['changed_at', 'changed_by', 'change_type', 'field_name']
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False


# ============================================================================
# BASE ADMIN CLASSES
# ============================================================================

class BaseModelAdmin(admin.ModelAdmin):
    """Base admin class with common functionality for models with timestamps"""
    
    def get_queryset(self, request):
        """Optimize queryset with select_related for foreign keys"""
        qs = super().get_queryset(request)
        return self._optimize_queryset(qs)
    
    def _optimize_queryset(self, qs):
        """Override this method in subclasses for specific optimizations"""
        return qs
    
    def get_readonly_fields(self, request, obj=None):
        """Make created_at and updated_at readonly if they exist"""
        readonly = list(super().get_readonly_fields(request, obj))
        
        # Only add timestamp fields if they exist on the model
        if hasattr(self.model, 'created_at'):
            readonly.append('created_at')
        if hasattr(self.model, 'updated_at'):
            readonly.append('updated_at')
            
        return readonly


class BaseLookupAdmin(BaseModelAdmin):
    """Base admin for lookup tables with is_active field"""
    list_display = ['name', 'code', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'code', 'description']
    actions = ['activate_selected', 'deactivate_selected']
    
    def activate_selected(self, request, queryset):
        queryset.update(is_active=True)
    activate_selected.short_description = "Activate selected records"
    
    def deactivate_selected(self, request, queryset):
        queryset.update(is_active=False)
    deactivate_selected.short_description = "Deactivate selected records"


class BaseReadOnlyLookupAdmin(BaseModelAdmin):
    """Base admin for lookup tables without is_active field"""
    list_display = ['name', 'code']
    search_fields = ['name', 'code', 'description']


# ============================================================================
# AREA ADMIN
# ============================================================================

class AreaAdmin(BaseLookupAdmin):
    """Admin for Area model with MPTT support"""
    list_display = ['name', 'administrative_level', 'code', 'parent_link', 
                   'get_children_count', 'is_active']
    list_filter = [AdministrativeLevelFilter, 'is_active']
    search_fields = ['name', 'code']
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'administrative_level', 'code', 'parent', 'is_active')
        }),
        ('Geographic Information', {
            'fields': ('latitude', 'longitude'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['created_at', 'updated_at']
    
    def parent_link(self, obj):
        if obj.parent:
            url = reverse('admin:core_area_change', args=[obj.parent.id])
            return format_html('<a href="{}">{}</a>', url, obj.parent.name)
        return '-'
    parent_link.short_description = 'Parent'
    
    def get_children_count(self, obj):
        count = obj.get_children().count()
        if count > 0:
            url = reverse('admin:core_area_changelist') + f'?parent__id__exact={obj.id}'
            return format_html('<a href="{}">{}</a>', url, count)
        return count
    get_children_count.short_description = 'Children'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('parent')


# ============================================================================
# DATA PROVIDER ADMIN
# ============================================================================

class DataProviderAdmin(BaseModelAdmin):
    """Admin for DataProvider model"""
    list_display = ['name', 'abbreviation', 'provider_type', 'contact_info', 
                   'dataset_count_display', 'is_active']
    list_filter = ['provider_type', 'data_access_policy', 'is_active', 
                  'has_quality_certification']
    search_fields = ['name', 'abbreviation', 'description', 'mandate']
    readonly_fields = ['created_at', 'updated_at', 'contact_count', 'dataset_count']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'abbreviation', 'provider_type', 'logo', 'is_active')
        }),
        ('Contact Information', {
            'fields': ('contact_person', 'email', 'phone', 'website', 'physical_address'),
            'classes': ('wide',)
        }),
        ('Organization Details', {
            'fields': ('headquarters_location', 'year_established', 'mandate', 'description'),
            'classes': ('collapse',)
        }),
        ('Data Collection', {
            'fields': ('data_collection_methods', 'sampling_framework', 'data_frequency'),
            'classes': ('collapse',)
        }),
        ('Quality Assurance', {
            'fields': ('has_quality_certification', 'quality_certification_details', 
                      'qa_procedures'),
            'classes': ('collapse',)
        }),
        ('Partnerships', {
            'fields': ('collaborating_institutions', 'funding_sources'),
            'classes': ('collapse',)
        }),
        ('Data Access', {
            'fields': ('data_access_policy', 'data_license', 'citation_recommendation'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('notes', 'created_at', 'updated_at', 'contact_count', 'dataset_count'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [ProviderContactInline, ProviderDatasetInline]
    
    def contact_info(self, obj):
        if obj.email:
            return format_html('<a href="mailto:{}">{}</a>', obj.email, obj.email)
        return obj.phone or '-'
    contact_info.short_description = 'Contact'
    
    def dataset_count_display(self, obj):
        count = obj.datasets.filter(is_active=True).count()
        if count > 0:
            url = reverse('admin:core_providerdataset_changelist') + f'?provider__id__exact={obj.id}'
            return format_html('<a href="{}">{}</a>', url, count)
        return count
    dataset_count_display.short_description = 'Datasets'
    dataset_count_display.admin_order_field = 'dataset_count'
    
    actions = ['activate_selected', 'deactivate_selected']
    
    def activate_selected(self, request, queryset):
        queryset.update(is_active=True)
    activate_selected.short_description = "Activate selected providers"
    
    def deactivate_selected(self, request, queryset):
        queryset.update(is_active=False)
    deactivate_selected.short_description = "Deactivate selected providers"
    
    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            dataset_count=Count('datasets', filter=Q(datasets__is_active=True))
        )


# ============================================================================
# SOURCE ADMIN
# ============================================================================

class SourceAdmin(BaseModelAdmin):
    """Admin for Source model"""
    list_display = ['name', 'provider_link', 'source_type', 'publication_year', 
                   'is_public', 'is_active']
    list_filter = ['source_type', 'is_public', 'is_active', YearFilter]
    search_fields = ['name', 'code', 'description']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'code', 'provider', 'source_type', 'is_public', 'is_active')
        }),
        ('Publication Details', {
            'fields': ('publication_year', 'access_url', 'description')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def provider_link(self, obj):
        url = reverse('admin:core_dataprovider_change', args=[obj.provider.id])
        return format_html('<a href="{}">{}</a>', url, obj.provider.name)
    provider_link.short_description = 'Provider'
    provider_link.admin_order_field = 'provider__name'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('provider')


# ============================================================================
# SECTOR/SUBSECTOR ADMIN
# ============================================================================

class SectorAdmin(BaseLookupAdmin):
    """Admin for Sector model"""
    list_display = ['name', 'code', 'subsector_count', 'display_order', 'is_active']
    inlines = [SubsectorInline]
    
    def subsector_count(self, obj):
        count = obj.subsectors.filter(is_active=True).count()
        if count > 0:
            url = reverse('admin:core_subsector_changelist') + f'?sector__id__exact={obj.id}'
            return format_html('<a href="{}">{}</a>', url, count)
        return count
    subsector_count.short_description = 'Subsectors'
    
    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            subsector_count=Count('subsectors', filter=Q(subsectors__is_active=True))
        )


class SubsectorAdmin(BaseLookupAdmin):
    """Admin for Subsector model with indicators inline"""
    list_display = ['name', 'sector_link', 'code', 'indicator_count', 'display_order', 'is_active']
    list_filter = ['sector', 'is_active']
    search_fields = ['name', 'code', 'sector__name']
    inlines = [IndicatorInline]
    
    def sector_link(self, obj):
        url = reverse('admin:core_sector_change', args=[obj.sector.id])
        return format_html('<a href="{}">{}</a>', url, obj.sector.name)
    sector_link.short_description = 'Sector'
    sector_link.admin_order_field = 'sector__name'
    
    def indicator_count(self, obj):
        count = obj.indicators.filter(is_active=True).count()
        if count > 0:
            url = reverse('admin:core_indicator_changelist') + f'?subsector__id__exact={obj.id}'
            return format_html('<a href="{}">{}</a>', url, count)
        return count
    indicator_count.short_description = 'Indicators'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('sector').annotate(
            indicator_count=Count('indicators', filter=Q(indicators__is_active=True))
        )


# ============================================================================
# DOMAIN ADMIN
# ============================================================================

class DomainAdmin(BaseReadOnlyLookupAdmin):
    """Admin for Domain model"""
    list_display = ['name', 'code', 'indicator_count', 'data_count']
    search_fields = ['name', 'code', 'description']
    
    def indicator_count(self, obj):
        count = obj.indicators.filter(is_active=True).count()
        if count > 0:
            url = reverse('admin:core_indicator_changelist') + f'?domain__id__exact={obj.id}'
            return format_html('<a href="{}">{}</a>', url, count)
        return count
    indicator_count.short_description = 'Indicators'
    
    def data_count(self, obj):
        count = obj.data_records.filter(is_active=True).count()
        if count > 0:
            url = reverse('admin:core_kilimostatdata_changelist') + f'?domain__id__exact={obj.id}'
            return format_html('<a href="{}">{}</a>', url, count)
        return count
    data_count.short_description = 'Data Records'
    
    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            indicator_count=Count('indicators', filter=Q(indicators__is_active=True)),
            data_count=Count('data_records', filter=Q(data_records__is_active=True))
        )


# ============================================================================
# UNIT ADMIN
# ============================================================================

class UnitAdmin(BaseReadOnlyLookupAdmin):
    """Admin for Unit model"""
    list_display = ['name', 'symbol', 'category', 'indicator_count', 'data_count']
    list_filter = ['category']
    search_fields = ['name', 'symbol', 'description']
    
    def indicator_count(self, obj):
        """Count indicators that use this unit"""
        count = obj.indicators.filter(is_active=True).count()
        if count > 0:
            url = reverse('admin:core_indicator_changelist') + f'?unit__id__exact={obj.id}'
            return format_html('<a href="{}">{}</a>', url, count)
        return count
    indicator_count.short_description = 'Indicators'
    
    def data_count(self, obj):
        """Count data records that use this unit"""
        count = obj.data_records.filter(is_active=True).count()
        if count > 0:
            url = reverse('admin:core_kilimostatdata_changelist') + f'?unit__id__exact={obj.id}'
            return format_html('<a href="{}">{}</a>', url, count)
        return count
    data_count.short_description = 'Data Records'
    
    def get_queryset(self, request):
        """Optimize queryset with annotations"""
        return super().get_queryset(request).annotate(
            indicator_count=Count('indicators', filter=Q(indicators__is_active=True)),
            data_count=Count('data_records', filter=Q(data_records__is_active=True))
        )


# ============================================================================
# SUBGROUP DIMENSION AND SUBGROUP ADMIN
# ============================================================================

class SubgroupDimensionAdmin(BaseReadOnlyLookupAdmin):
    """Admin for SubgroupDimension model"""
    list_display = ['name', 'code', 'subgroup_count', 'indicator_count']
    search_fields = ['name', 'code', 'description']
    inlines = [SubgroupInline]
    
    def subgroup_count(self, obj):
        return obj.subgroups.count()
    subgroup_count.short_description = 'Subgroups'
    
    def indicator_count(self, obj):
        """Count indicators in this dimension through subgroups"""
        return Indicator.objects.filter(subgroup__dimension=obj, is_active=True).count()
    indicator_count.short_description = 'Indicators'


class SubgroupAdmin(BaseReadOnlyLookupAdmin):
    """Admin for Subgroup model"""
    list_display = ['name', 'dimension_link', 'code', 'indicator_count', 'data_count']
    list_filter = ['dimension']
    search_fields = ['name', 'code', 'dimension__name']
    
    def dimension_link(self, obj):
        url = reverse('admin:core_subgroupdimension_change', args=[obj.dimension.id])
        return format_html('<a href="{}">{}</a>', url, obj.dimension.name)
    dimension_link.short_description = 'Dimension'
    dimension_link.admin_order_field = 'dimension__name'
    
    def indicator_count(self, obj):
        count = obj.indicators.filter(is_active=True).count()
        if count > 0:
            url = reverse('admin:core_indicator_changelist') + f'?subgroup__id__exact={obj.id}'
            return format_html('<a href="{}">{}</a>', url, count)
        return count
    indicator_count.short_description = 'Indicators'
    
    def data_count(self, obj):
        count = obj.data_records.filter(is_active=True).count()
        if count > 0:
            url = reverse('admin:core_kilimostatdata_changelist') + f'?subgroup__id__exact={obj.id}'
            return format_html('<a href="{}">{}</a>', url, count)
        return count
    data_count.short_description = 'Data Records'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('dimension').annotate(
            indicator_count=Count('indicators', filter=Q(indicators__is_active=True))
        )


# ============================================================================
# INDICATOR ADMIN
# ============================================================================

class IndicatorAdmin(BaseLookupAdmin):
    """Admin for Indicator model with all relationships"""
    list_display = ['name', 'code', 'domain_link', 'subsector_link', 'subgroup_link', 
                   'unit_link', 'is_core_indicator', 'data_count', 'is_active']
    list_filter = [
        'is_core_indicator', 'is_active', 
        IndicatorDomainFilter, 
        IndicatorSubsectorFilter, 
        IndicatorSubgroupFilter,
        IndicatorUnitFilter
    ]
    search_fields = ['name', 'code', 'description', 'domain__name', 'subsector__name', 'unit__name']
    readonly_fields = ['created_at', 'updated_at', 'data_count']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'code', 'is_core_indicator', 'is_active')
        }),
        ('Relationships', {
            'fields': ('domain', 'subsector', 'subgroup', 'unit'),
            'classes': ('wide',)
        }),
        ('Description', {
            'fields': ('description',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at', 'data_count'),
            'classes': ('collapse',)
        }),
    )
    
    def domain_link(self, obj):
        if obj.domain:
            url = reverse('admin:core_domain_change', args=[obj.domain.id])
            return format_html('<a href="{}">{}</a>', url, obj.domain.name)
        return '-'
    domain_link.short_description = 'Domain'
    domain_link.admin_order_field = 'domain__name'
    
    def subsector_link(self, obj):
        if obj.subsector:
            url = reverse('admin:core_subsector_change', args=[obj.subsector.id])
            return format_html('<a href="{}">{}</a>', url, obj.subsector.name)
        return '-'
    subsector_link.short_description = 'Subsector'
    subsector_link.admin_order_field = 'subsector__name'
    
    def subgroup_link(self, obj):
        if obj.subgroup:
            url = reverse('admin:core_subgroup_change', args=[obj.subgroup.id])
            return format_html('<a href="{}">{}</a>', url, obj.subgroup.name)
        return '-'
    subgroup_link.short_description = 'Subgroup'
    subgroup_link.admin_order_field = 'subgroup__name'
    
    def unit_link(self, obj):
        if obj.unit:
            url = reverse('admin:core_unit_change', args=[obj.unit.id])
            return format_html('<a href="{}">{}</a>', url, obj.unit.name)
        return '-'
    unit_link.short_description = 'Unit'
    unit_link.admin_order_field = 'unit__name'
    
    def data_count(self, obj):
        count = obj.data_records.filter(is_active=True).count()
        if count > 0:
            url = reverse('admin:core_kilimostatdata_changelist') + f'?indicator__id__exact={obj.id}'
            return format_html('<a href="{}">{}</a>', url, count)
        return count
    data_count.short_description = 'Data Records'
    
    actions = ['mark_as_core', 'mark_as_non_core']
    
    def mark_as_core(self, request, queryset):
        queryset.update(is_core_indicator=True)
    mark_as_core.short_description = "Mark as core indicators"
    
    def mark_as_non_core(self, request, queryset):
        queryset.update(is_core_indicator=False)
    mark_as_non_core.short_description = "Mark as non-core indicators"
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'domain', 'subsector', 'subgroup', 'unit'
        ).annotate(
            data_count=Count('data_records', filter=Q(data_records__is_active=True))
        )


# ============================================================================
# ITEM CATEGORY AND ITEM ADMIN
# ============================================================================

class ItemCategoryAdmin(BaseReadOnlyLookupAdmin):
    """Admin for ItemCategory model"""
    list_display = ['name', 'code', 'item_count', 'display_order']
    search_fields = ['name', 'code', 'description']
    inlines = [ItemInline]
    
    def item_count(self, obj):
        count = obj.items.filter(is_active=True).count()
        if count > 0:
            url = reverse('admin:core_item_changelist') + f'?category__id__exact={obj.id}'
            return format_html('<a href="{}">{}</a>', url, count)
        return count
    item_count.short_description = 'Items'


class ItemAdmin(BaseLookupAdmin):
    """Admin for Item model"""
    list_display = ['name', 'category_link', 'code', 'data_count', 'is_active']
    list_filter = ['category', 'is_active']
    search_fields = ['name', 'code', 'category__name']
    
    def category_link(self, obj):
        if obj.category:
            url = reverse('admin:core_itemcategory_change', args=[obj.category.id])
            return format_html('<a href="{}">{}</a>', url, obj.category.name)
        return '-'
    category_link.short_description = 'Category'
    category_link.admin_order_field = 'category__name'
    
    def data_count(self, obj):
        count = obj.data_records.filter(is_active=True).count()
        if count > 0:
            url = reverse('admin:core_kilimostatdata_changelist') + f'?item__id__exact={obj.id}'
            return format_html('<a href="{}">{}</a>', url, count)
        return count
    data_count.short_description = 'Data Records'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('category')


# ============================================================================
# PROVIDER CONTACT AND DATASET ADMIN
# ============================================================================

class ProviderContactAdmin(admin.ModelAdmin):
    """Admin for ProviderContact model"""
    list_display = ['name', 'provider_link', 'position', 'email_link', 'phone', 'is_primary']
    list_filter = ['is_primary', 'provider']
    search_fields = ['name', 'email', 'position', 'provider__name']
    readonly_fields = ['created_at', 'updated_at']
    
    def provider_link(self, obj):
        url = reverse('admin:core_dataprovider_change', args=[obj.provider.id])
        return format_html('<a href="{}">{}</a>', url, obj.provider.name)
    provider_link.short_description = 'Provider'
    provider_link.admin_order_field = 'provider__name'
    
    def email_link(self, obj):
        if obj.email:
            return format_html('<a href="mailto:{}">{}</a>', obj.email, obj.email)
        return '-'
    email_link.short_description = 'Email'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('provider')


class ProviderDatasetAdmin(admin.ModelAdmin):
    """Admin for ProviderDataset model"""
    list_display = ['name', 'provider_link', 'release_date', 'version', 
                   'last_update', 'is_active']
    list_filter = ['is_active', YearFilter]
    search_fields = ['name', 'description', 'provider__name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('provider', 'name', 'version', 'release_date', 'last_update', 'is_active')
        }),
        ('Description', {
            'fields': ('description', 'methodology', 'citation')
        }),
        ('Coverage', {
            'fields': ('geographic_coverage', 'temporal_coverage'),
            'classes': ('collapse',)
        }),
        ('Access', {
            'fields': ('url',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def provider_link(self, obj):
        url = reverse('admin:core_dataprovider_change', args=[obj.provider.id])
        return format_html('<a href="{}">{}</a>', url, obj.provider.name)
    provider_link.short_description = 'Provider'
    provider_link.admin_order_field = 'provider__name'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('provider')


# ============================================================================
# KILIMOSTAT DATA ADMIN
# ============================================================================

class KilimoSTATDataAdminForm(forms.ModelForm):
    """Custom form for KilimoSTATData with validation"""
    
    class Meta:
        model = KilimoSTATData
        fields = '__all__'
    
    def clean(self):
        cleaned_data = super().clean()
        subgroup_dimension = cleaned_data.get('subgroup_dimension')
        subgroup = cleaned_data.get('subgroup')
        
        if (subgroup_dimension is None) != (subgroup is None):
            raise forms.ValidationError(
                "Both subgroup_dimension and subgroup must be set together or both null"
            )
        
        return cleaned_data


class KilimoSTATDataAdmin(ImportExportModelAdmin):
    """Admin for KilimoSTATData with import/export functionality"""
    resource_class = KilimoSTATDataResource
    form = KilimoSTATDataAdminForm
    
    list_display = ['indicator', 'area', 'time_period', 'data_value', 
                   'unit', 'flag', 'quality_badge', 'is_active']
    list_filter = [
        'sector', 'indicator__is_core_indicator', 'indicator__subsector',
        'area__administrative_level', 'time_period', 'flag', 'is_active', 
        'domain', 'unit'
    ]
    search_fields = [
        'indicator__name', 'area__name', 'notes', 'slug',
        'item__name', 'source__name'
    ]
    readonly_fields = ['slug', 'created_at', 'updated_at', 'metadata_link']
    
    fieldsets = (
        ('Core Data', {
            'fields': (
                'area', 'source', 'provider', 'sector', 'subsector',
                'indicator', 'item', 'domain', 'unit'
            )
        }),
        ('Subgroup Information', {
            'fields': ('subgroup_dimension', 'subgroup'),
            'classes': ('wide',)
        }),
        ('Values', {
            'fields': ('time_period', 'data_value', 'flag')
        }),
        ('Confidence Intervals', {
            'fields': ('confidence_lower', 'confidence_upper', 'standard_error', 'sample_size'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('slug', 'notes', 'is_active', 'created_by', 
                      'created_at', 'updated_at', 'metadata_link'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [MetadataInline]
    actions = ['activate_selected', 'deactivate_selected', 'export_as_json']
    
    # Import/Export configuration
    tmp_storage_class = TempFolderStorage
    import_template_name = 'admin/import_export/import.html'
    export_template_name = 'admin/import_export/export.html'
    
    def get_export_filename(self, request, queryset, file_format):
        """Custom export filename"""
        date_str = timezone.now().strftime('%Y%m%d_%H%M%S')
        return f'kilimostat_data_export_{date_str}.{file_format.get_extension()}'
    
    def get_import_form(self):
        """Return the import form class"""
        return KilimoSTATDataAdminForm
    
    def get_import_data_kwargs(self, request, *args, **kwargs):
        """Additional kwargs for import_data"""
        return {
            'dry_run': request.POST.get('dry_run') == '1',
        }
    
    def quality_badge(self, obj):
        metadata = obj.get_metadata()
        if metadata and metadata.quality_score:
            score = metadata.quality_score
            if score >= 90:
                color = 'green'
                text = f'Excellent ({score})'
            elif score >= 75:
                color = 'blue'
                text = f'Good ({score})'
            elif score >= 60:
                color = 'orange'
                text = f'Fair ({score})'
            else:
                color = 'red'
                text = f'Poor ({score})'
            
            return format_html(
                '<span style="color: {}; font-weight: bold;">{}</span>',
                color, text
            )
        return '-'
    quality_badge.short_description = 'Quality'
    
    def metadata_link(self, obj):
        metadata = obj.get_metadata()
        if metadata:
            url = reverse('admin:core_metadata_change', args=[metadata.pk])
            return format_html('<a href="{}">View Metadata (v{})</a>', url, metadata.version)
        return 'No metadata'
    metadata_link.short_description = 'Metadata'
    
    def activate_selected(self, request, queryset):
        queryset.update(is_active=True)
    activate_selected.short_description = "Activate selected records"
    
    def deactivate_selected(self, request, queryset):
        queryset.update(is_active=False)
    deactivate_selected.short_description = "Deactivate selected records"
    
    def export_as_json(self, request, queryset):
        """Export selected records as JSON"""
        data = []
        for record in queryset.select_related(
            'area', 'indicator', 'unit', 'sector'
        ).prefetch_related('metadata'):
            record_data = {
                'id': record.id,
                'area': record.area.name,
                'indicator': record.indicator.name,
                'time_period': record.time_period,
                'value': record.data_value,
                'unit': record.unit.symbol or record.unit.name,
                'sector': record.sector.name,
                'flag': record.flag,
            }
            
            metadata = record.get_metadata()
            if metadata:
                record_data['quality_score'] = metadata.quality_score
                record_data['quality_category'] = metadata.quality_category
            
            data.append(record_data)
        
        from django.http import JsonResponse
        response = JsonResponse(data, safe=False)
        response['Content-Disposition'] = 'attachment; filename="kilimostat_export.json"'
        return response
    export_as_json.short_description = "Export selected as JSON"
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'area', 'source', 'provider', 'sector', 'subsector',
            'indicator', 'item', 'domain', 'unit', 'subgroup_dimension', 'subgroup'
        )


# ============================================================================
# INDICATOR METADATA ADMIN
# ============================================================================

class IndicatorMetadataAdmin(admin.ModelAdmin):
    """Admin for IndicatorMetadata model"""
    list_display = ['indicator_link', 'sector', 'sub_sector', 'unit', 'is_active']
    list_filter = ['sector', 'sub_sector', 'unit', 'is_active']
    search_fields = ['indicator__name', 'definition', 'relevance']
    readonly_fields = ['slug', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('indicator', 'slug', 'sector', 'sub_sector', 'unit', 'is_active')
        }),
        ('Definition', {
            'fields': ('definition', 'relevance')
        }),
        ('Methodology', {
            'fields': ('calculation', 'treatment_of_missing_values', 'disaggregation'),
            'classes': ('collapse',)
        }),
        ('Source', {
            'fields': ('data_provider', 'source_hyperlink', 'source_description'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def indicator_link(self, obj):
        url = reverse('admin:core_indicator_change', args=[obj.indicator.id])
        return format_html('<a href="{}">{}</a>', url, obj.indicator.name)
    indicator_link.short_description = 'Indicator'
    indicator_link.admin_order_field = 'indicator__name'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'indicator', 'sector', 'sub_sector', 'unit', 'data_provider'
        )


# ============================================================================
# FREQUENCY AND LICENSE ADMIN
# ============================================================================

class FrequencyAdmin(BaseReadOnlyLookupAdmin):
    """Admin for Frequency model"""
    list_display = ['name', 'code', 'usage_count']
    search_fields = ['name', 'code', 'description']
    
    def usage_count(self, obj):
        return obj.metadata_records.count()
    usage_count.short_description = 'Times Used'


class LicenseAdmin(BaseReadOnlyLookupAdmin):
    """Admin for License model"""
    list_display = ['name', 'code', 'url', 'usage_count']
    search_fields = ['name', 'code', 'description']
    
    def usage_count(self, obj):
        return obj.metadata_records.count()
    usage_count.short_description = 'Times Used'


# ============================================================================
# METADATA ADMIN
# ============================================================================

class MetadataAdmin(admin.ModelAdmin):
    """Admin for Metadata model"""
    list_display = ['data_record_link', 'version', 'quality_score', 'quality_category',
                   'review_status', 'is_latest_version', 'published_at']
    list_filter = [
        'quality_category', 'review_status', 'provenance_level',
        'access_level', 'is_latest_version', DataQualityFilter
    ]
    search_fields = [
        'data_record__indicator__name', 'data_record__area__name',
        'record_identifier', 'keywords'
    ]
    readonly_fields = ['uuid', 'created_at', 'updated_at', 'derived_from_link']
    
    fieldsets = (
        ('Basic Metadata', {
            'fields': ('data_record', 'metadata_version', 'uuid', 'record_identifier',
                      'published_at', 'embargo_until')
        }),
        ('Indicator Metadata', {
            'fields': ('indicator_metadata',)
        }),
        ('Provenance', {
            'fields': ('provenance_level', 'original_source_name', 'original_source_url',
                      'original_source_id', 'original_data_location', 'processing_notes',
                      'derived_from'),
            'classes': ('collapse',)
        }),
        ('Quality Metrics', {
            'fields': ('quality_score', 'quality_category', 'completeness',
                      'accuracy', 'consistency', 'quality_notes', 'quality_check_date'),
            'classes': ('collapse',)
        }),
        ('Methodology', {
            'fields': ('methodology_type', 'methodology_description', 'methodology_url',
                      'sample_size', 'sampling_error', 'response_rate'),
            'classes': ('collapse',)
        }),
        ('Statistical Properties', {
            'fields': ('mean', 'median', 'standard_deviation', 'range_min', 'range_max',
                      'confidence_level', 'confidence_interval_lower', 'confidence_interval_upper'),
            'classes': ('collapse',)
        }),
        ('Temporal Information', {
            'fields': ('time_type', 'reference_period_start', 'reference_period_end',
                      'reference_period_description', 'frequency'),
            'classes': ('collapse',)
        }),
        ('Geographic Information', {
            'fields': ('geographic_level', 'geographic_scope', 'spatial_resolution'),
            'classes': ('collapse',)
        }),
        ('Access & Usage', {
            'fields': ('access_level', 'license', 'license_url', 'citation_recommendation',
                      'download_count', 'view_count', 'last_accessed'),
            'classes': ('collapse',)
        }),
        ('Review & Validation', {
            'fields': ('review_status', 'review_date', 'reviewed_by', 'reviewer_notes',
                      'approved_by', 'approval_date'),
            'classes': ('collapse',)
        }),
        ('Versioning', {
            'fields': ('version', 'previous_version', 'version_notes', 'is_latest_version'),
            'classes': ('collapse',)
        }),
        ('Contact', {
            'fields': ('data_owner', 'contact_email'),
            'classes': ('collapse',)
        }),
        ('Tags & Classifications', {
            'fields': ('keywords', 'sdg_goals', 'is_official_statistic'),
            'classes': ('collapse',)
        }),
        ('Custom Fields', {
            'fields': ('custom_metadata',),
            'classes': ('collapse',)
        }),
        ('Audit', {
            'fields': ('created_by', 'modified_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [MetadataChangeLogInline]
    
    def data_record_link(self, obj):
        url = reverse('admin:core_kilimostatdata_change', args=[obj.data_record.id])
        return format_html('<a href="{}">{}</a>', url, str(obj.data_record))
    data_record_link.short_description = 'Data Record'
    data_record_link.admin_order_field = 'data_record'
    
    def derived_from_link(self, obj):
        if obj.pk:
            links = []
            for derived in obj.derived_from.all():
                url = reverse('admin:core_metadata_change', args=[derived.pk])
                links.append(f'<a href="{url}">{derived.record_identifier}</a>')
            return format_html(', '.join(links)) if links else '-'
        return '-'
    derived_from_link.short_description = 'Derived From'
    
    actions = ['approve_selected', 'set_as_latest_version']
    
    def approve_selected(self, request, queryset):
        queryset.update(
            review_status='approved',
            approved_by=request.user.username,
            approval_date=timezone.now().date()
        )
    approve_selected.short_description = "Approve selected metadata records"
    
    def set_as_latest_version(self, request, queryset):
        # First set all to not latest
        if queryset.count() > 0:
            data_record_ids = queryset.values_list('data_record_id', flat=True).distinct()
            Metadata.objects.filter(data_record_id__in=data_record_ids).update(is_latest_version=False)
            
            # Then set selected as latest
            queryset.update(is_latest_version=True)
    set_as_latest_version.short_description = "Set as latest version"
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'data_record', 'indicator_metadata', 'frequency', 'license'
        )


# ============================================================================
# METADATA CHANGE LOG ADMIN
# ============================================================================

class MetadataChangeLogAdmin(admin.ModelAdmin):
    """Admin for MetadataChangeLog model"""
    list_display = ['metadata_link', 'changed_at', 'changed_by', 'change_type', 'field_name']
    list_filter = ['change_type', 'changed_by']
    search_fields = ['metadata__record_identifier', 'changed_by', 'field_name']
    readonly_fields = ['changed_at']
    
    def metadata_link(self, obj):
        url = reverse('admin:core_metadata_change', args=[obj.metadata.pk])
        return format_html('<a href="{}">{}</a>', url, obj.metadata.record_identifier)
    metadata_link.short_description = 'Metadata'
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('metadata')


# ============================================================================
# REGISTER MODELS WITH ADMIN
# ============================================================================

admin.site.register(Area, AreaAdmin)
admin.site.register(DataProvider, DataProviderAdmin)
admin.site.register(Source, SourceAdmin)
admin.site.register(Sector, SectorAdmin)
admin.site.register(Subsector, SubsectorAdmin)
admin.site.register(Domain, DomainAdmin)
admin.site.register(Unit, UnitAdmin)
admin.site.register(SubgroupDimension, SubgroupDimensionAdmin)
admin.site.register(Subgroup, SubgroupAdmin)
admin.site.register(Indicator, IndicatorAdmin)
admin.site.register(ItemCategory, ItemCategoryAdmin)
admin.site.register(Item, ItemAdmin)
admin.site.register(ProviderContact, ProviderContactAdmin)
admin.site.register(ProviderDataset, ProviderDatasetAdmin)
admin.site.register(KilimoSTATData, KilimoSTATDataAdmin)
admin.site.register(IndicatorMetadata, IndicatorMetadataAdmin)
admin.site.register(Frequency, FrequencyAdmin)
admin.site.register(License, LicenseAdmin)
admin.site.register(Metadata, MetadataAdmin)
admin.site.register(MetadataChangeLog, MetadataChangeLogAdmin)


# ============================================================================
# CUSTOM ADMIN SITE CONFIGURATION
# ============================================================================

admin.site.site_header = 'KilimoSTAT Administration'
admin.site.site_title = 'KilimoSTAT Admin'
admin.site.index_title = 'Food Systems Data Management'