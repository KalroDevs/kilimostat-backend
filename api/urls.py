from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token

# Import drf-spectacular views
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

# Import views from your views modules - NOT from api.urls
from api.views.lookup_views import (
    AreaViewSet, DataProviderViewSet, ProviderContactViewSet,
    ProviderDatasetViewSet, SourceViewSet, SectorViewSet,
    SubsectorViewSet, IndicatorViewSet, ItemCategoryViewSet,
    ItemViewSet, DomainViewSet, UnitViewSet, SubgroupDimensionViewSet,
    SubgroupViewSet
)
from api.views.kilimo_data_views import (
    KilimoSTATDataViewSet, StatisticsView
)
from api.views.metadata_views import (
    FrequencyViewSet, LicenseViewSet, IndicatorMetadataViewSet,
    MetadataViewSet, MetadataChangeLogViewSet
)

# Create main router
router = DefaultRouter()

# Area
router.register(r'areas', AreaViewSet, basename='area')

# Data Provider
router.register(r'providers', DataProviderViewSet, basename='dataprovider')
router.register(r'provider-contacts', ProviderContactViewSet, basename='providercontact')
router.register(r'provider-datasets', ProviderDatasetViewSet, basename='providerdataset')

# Source
router.register(r'sources', SourceViewSet, basename='source')

# Sector/Subsector
router.register(r'sectors', SectorViewSet, basename='sector')
router.register(r'subsectors', SubsectorViewSet, basename='subsector')

# Indicator
router.register(r'indicators', IndicatorViewSet, basename='indicator')

# Item
router.register(r'item-categories', ItemCategoryViewSet, basename='itemcategory')
router.register(r'items', ItemViewSet, basename='item')

# Domain
router.register(r'domains', DomainViewSet, basename='domain')

# Unit
router.register(r'units', UnitViewSet, basename='unit')

# Subgroup
router.register(r'subgroup-dimensions', SubgroupDimensionViewSet, basename='subgroupdimension')
router.register(r'subgroups', SubgroupViewSet, basename='subgroup')

# KilimoSTAT Data
router.register(r'data', KilimoSTATDataViewSet, basename='kilimostatdata')

# Metadata
router.register(r'frequencies', FrequencyViewSet, basename='frequency')
router.register(r'licenses', LicenseViewSet, basename='license')
router.register(r'indicator-metadata', IndicatorMetadataViewSet, basename='indicatormetadata')
router.register(r'metadata', MetadataViewSet, basename='metadata')
router.register(r'metadata-changelogs', MetadataChangeLogViewSet, basename='metadatachangelog')

urlpatterns = [
    # API root
    path('', include(router.urls)),
    
    # Authentication
    path('auth/', include('rest_framework.urls')),
    path('auth/token/', obtain_auth_token, name='api_token_auth'),
    
    # Statistics
    path('statistics/', StatisticsView.as_view(), name='statistics'),
    
    # OpenAPI schema (JSON)
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    
    # Swagger UI
    path('swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    
    # ReDoc UI
    path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]