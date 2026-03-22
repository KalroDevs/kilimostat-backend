from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404




from core.models import (
    Area, DataProvider, ProviderContact, ProviderDataset,
    Source, Sector, Subsector, Indicator, ItemCategory, Item,
    Domain, Unit, SubgroupDimension, Subgroup
)
from api.serializers import (
    AreaSerializer, AreaDetailSerializer, DataProviderSerializer,
    DataProviderDetailSerializer, ProviderContactSerializer,
    ProviderDatasetSerializer, SourceSerializer, SectorSerializer,
    SectorDetailSerializer, SubsectorSerializer, IndicatorSerializer,
    ItemCategorySerializer, ItemSerializer, DomainSerializer,
    UnitSerializer, SubgroupDimensionSerializer,
    SubgroupDimensionDetailSerializer, SubgroupSerializer
)
from api.filters import (
    AreaFilter, DataProviderFilter, ProviderContactFilter,
    ProviderDatasetFilter, SourceFilter, SectorFilter,
    SubsectorFilter, IndicatorFilter, ItemFilter, UnitFilter,
    SubgroupFilter
)



from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiExample

@extend_schema_view(
    list=extend_schema(
        summary="List all areas",
        description="Returns a list of all geographic areas with optional filtering",
        tags=['areas'],
    ),
    retrieve=extend_schema(
        summary="Retrieve an area",
        description="Returns detailed information about a specific area including its children",
        tags=['areas'],
    ),
    ancestors=extend_schema(
        summary="Get area ancestors",
        description="Returns all ancestor areas in the hierarchy",
        tags=['areas'],
    ),
    descendants=extend_schema(
        summary="Get area descendants",
        description="Returns all descendant areas in the hierarchy",
        tags=['areas'],
    ),
    roots=extend_schema(
        summary="Get root areas",
        description="Returns all top-level areas (with no parent)",
        tags=['areas'],
    ),
)

# ============================================================================
# AREA VIEWSET
# ============================================================================

class AreaViewSet(viewsets.ModelViewSet):
    """ViewSet for Area model"""
    queryset = Area.objects.all()
    serializer_class = AreaSerializer
    filterset_class = AreaFilter
    search_fields = ['name', 'code']
    ordering_fields = ['name', 'administrative_level', 'created_at']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return AreaDetailSerializer
        return AreaSerializer
    
    @action(detail=True, methods=['get'])
    def ancestors(self, request, pk=None):
        """Get ancestors of an area"""
        area = self.get_object()
        ancestors = area.get_ancestors()
        serializer = self.get_serializer(ancestors, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def descendants(self, request, pk=None):
        """Get descendants of an area"""
        area = self.get_object()
        descendants = area.get_descendants()
        serializer = self.get_serializer(descendants, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def roots(self, request):
        """Get root areas (no parent)"""
        roots = Area.objects.filter(parent__isnull=True)
        serializer = self.get_serializer(roots, many=True)
        return Response(serializer.data)


# ============================================================================
# DATA PROVIDER VIEWSET
# ============================================================================

class DataProviderViewSet(viewsets.ModelViewSet):
    """ViewSet for DataProvider model"""
    queryset = DataProvider.objects.all().annotate(
        contact_count=Count('contacts', distinct=True),
        dataset_count=Count('datasets', filter=Q(datasets__is_active=True), distinct=True)
    )
    serializer_class = DataProviderSerializer
    filterset_class = DataProviderFilter
    search_fields = ['name', 'abbreviation', 'description', 'mandate']
    ordering_fields = ['name', 'provider_type', 'created_at', 'dataset_count']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return DataProviderDetailSerializer
        return DataProviderSerializer
    
    @action(detail=True, methods=['get'])
    def contacts(self, request, pk=None):
        """Get contacts for a provider"""
        provider = self.get_object()
        contacts = provider.contacts.all()
        serializer = ProviderContactSerializer(contacts, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def datasets(self, request, pk=None):
        """Get datasets for a provider"""
        provider = self.get_object()
        datasets = provider.datasets.filter(is_active=True)
        serializer = ProviderDatasetSerializer(datasets, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def sources(self, request, pk=None):
        """Get sources for a provider"""
        provider = self.get_object()
        sources = provider.sources.filter(is_active=True)
        serializer = SourceSerializer(sources, many=True)
        return Response(serializer.data)


class ProviderContactViewSet(viewsets.ModelViewSet):
    """ViewSet for ProviderContact model"""
    queryset = ProviderContact.objects.all()
    serializer_class = ProviderContactSerializer
    filterset_class = ProviderContactFilter
    search_fields = ['name', 'email', 'position']
    ordering_fields = ['name', 'is_primary', 'created_at']


class ProviderDatasetViewSet(viewsets.ModelViewSet):
    """ViewSet for ProviderDataset model"""
    queryset = ProviderDataset.objects.all()
    serializer_class = ProviderDatasetSerializer
    filterset_class = ProviderDatasetFilter
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'release_date', 'last_update', 'created_at']


# ============================================================================
# SOURCE VIEWSET
# ============================================================================

class SourceViewSet(viewsets.ModelViewSet):
    """ViewSet for Source model"""
    queryset = Source.objects.all().select_related('provider')
    serializer_class = SourceSerializer
    filterset_class = SourceFilter
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['name', 'publication_year', 'source_type', 'created_at']


# ============================================================================
# SECTOR/SUBSECTOR VIEWSETS
# ============================================================================

class SectorViewSet(viewsets.ModelViewSet):
    """ViewSet for Sector model"""
    queryset = Sector.objects.all().annotate(
        subsector_count=Count('subsectors', filter=Q(subsectors__is_active=True))
    )
    serializer_class = SectorSerializer
    filterset_class = SectorFilter
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['name', 'display_order', 'created_at']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return SectorDetailSerializer
        return SectorSerializer
    
    @action(detail=True, methods=['get'])
    def subsectors(self, request, pk=None):
        """Get subsectors for a sector"""
        sector = self.get_object()
        subsectors = sector.subsectors.filter(is_active=True)
        serializer = SubsectorSerializer(subsectors, many=True)
        return Response(serializer.data)


class SubsectorViewSet(viewsets.ModelViewSet):
    """ViewSet for Subsector model"""
    queryset = Subsector.objects.all().select_related('sector')
    serializer_class = SubsectorSerializer
    filterset_class = SubsectorFilter
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['name', 'display_order', 'created_at']


# ============================================================================
# INDICATOR VIEWSET
# ============================================================================

class IndicatorViewSet(viewsets.ModelViewSet):
    """ViewSet for Indicator model"""
    queryset = Indicator.objects.all().annotate(
        data_count=Count('data_records', filter=Q(data_records__is_active=True))
    )
    serializer_class = IndicatorSerializer
    filterset_class = IndicatorFilter
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['name', 'indicator_type', 'is_core_indicator', 'created_at']
    
    @action(detail=True, methods=['get'])
    def data(self, request, pk=None):
        """Get data records for an indicator"""
        indicator = self.get_object()
        data_records = indicator.data_records.filter(is_active=True)
        
        # Apply query parameters
        area = request.query_params.get('area')
        if area:
            data_records = data_records.filter(area_id=area)
        
        year = request.query_params.get('year')
        if year:
            data_records = data_records.filter(time_period=year)
        
        from api.serializers import KilimoSTATDataSerializer
        serializer = KilimoSTATDataSerializer(data_records, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def metadata(self, request, pk=None):
        """Get metadata for an indicator"""
        indicator = self.get_object()
        try:
            metadata = indicator.metadata
            from api.serializers import IndicatorMetadataSerializer
            serializer = IndicatorMetadataSerializer(metadata)
            return Response(serializer.data)
        except Indicator.metadata.RelatedObjectDoesNotExist:
            return Response(
                {'detail': 'No metadata found for this indicator'}, 
                status=status.HTTP_404_NOT_FOUND
            )


# ============================================================================
# ITEM VIEWSETS
# ============================================================================

class ItemCategoryViewSet(viewsets.ModelViewSet):
    """ViewSet for ItemCategory model"""
    queryset = ItemCategory.objects.all().annotate(
        item_count=Count('items', filter=Q(items__is_active=True))
    )
    serializer_class = ItemCategorySerializer
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['name', 'display_order']
    
    @action(detail=True, methods=['get'])
    def items(self, request, pk=None):
        """Get items in a category"""
        category = self.get_object()
        items = category.items.filter(is_active=True)
        serializer = ItemSerializer(items, many=True)
        return Response(serializer.data)


class ItemViewSet(viewsets.ModelViewSet):
    """ViewSet for Item model"""
    queryset = Item.objects.all().select_related('category').annotate(
        data_count=Count('data_records', filter=Q(data_records__is_active=True))
    )
    serializer_class = ItemSerializer
    filterset_class = ItemFilter
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['name', 'category', 'created_at']


# ============================================================================
# DOMAIN VIEWSET
# ============================================================================

class DomainViewSet(viewsets.ModelViewSet):
    """ViewSet for Domain model"""
    queryset = Domain.objects.all().annotate(
        data_count=Count('data_records', filter=Q(data_records__is_active=True))
    )
    serializer_class = DomainSerializer
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['name', 'created_at']


# ============================================================================
# UNIT VIEWSET
# ============================================================================

class UnitViewSet(viewsets.ModelViewSet):
    """ViewSet for Unit model"""
    queryset = Unit.objects.all().annotate(
        # Count indicators through IndicatorMetadata (if needed)
        indicator_count=Count('indicatormetadata', filter=Q(indicatormetadata__is_active=True), distinct=True),
        # Count data records directly from KilimoSTATData
        data_count=Count('data_records', filter=Q(data_records__is_active=True), distinct=True)
    )
    serializer_class = UnitSerializer
    filterset_class = UnitFilter
    search_fields = ['name', 'symbol', 'description']
    ordering_fields = ['name', 'category', 'created_at']
# ============================================================================
# SUBGROUP VIEWSETS
# ============================================================================

class SubgroupDimensionViewSet(viewsets.ModelViewSet):
    """ViewSet for SubgroupDimension model"""
    queryset = SubgroupDimension.objects.all().annotate(
        subgroup_count=Count('subgroups')
    )
    serializer_class = SubgroupDimensionSerializer
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['name', 'created_at']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return SubgroupDimensionDetailSerializer
        return SubgroupDimensionSerializer
    
    @action(detail=True, methods=['get'])
    def subgroups(self, request, pk=None):
        """Get subgroups in a dimension"""
        dimension = self.get_object()
        subgroups = dimension.subgroups.all()
        serializer = SubgroupSerializer(subgroups, many=True)
        return Response(serializer.data)


class SubgroupViewSet(viewsets.ModelViewSet):
    """ViewSet for Subgroup model"""
    queryset = Subgroup.objects.all().select_related('dimension').annotate(
        data_count=Count('data_records', filter=Q(data_records__is_active=True))
    )
    serializer_class = SubgroupSerializer
    filterset_class = SubgroupFilter
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['name', 'dimension', 'created_at']