import django_filters
from django_filters import rest_framework as filters
from core.models import *
from django.db.models import Q

class KilimoSTATDataFilter(filters.FilterSet):
    """
    Advanced filters for KilimoSTATData
    """
    # Range filters
    min_value = filters.NumberFilter(field_name="data_value", lookup_expr='gte')
    max_value = filters.NumberFilter(field_name="data_value", lookup_expr='lte')
    
    # Date/Time filters
    year = filters.CharFilter(field_name="time_period", lookup_expr='icontains')
    year_min = filters.CharFilter(field_name="time_period", method='filter_year_min')
    year_max = filters.CharFilter(field_name="time_period", method='filter_year_max')
    
    # Multiple choice filters
    areas = filters.ModelMultipleChoiceFilter(
        field_name="area",
        queryset=Area.objects.all(),
        conjoined=False
    )
    indicators = filters.ModelMultipleChoiceFilter(
        field_name="indicator",
        queryset=Indicator.objects.all(),
        conjoined=False
    )
    sectors = filters.ModelMultipleChoiceFilter(
        field_name="sector",
        queryset=Sector.objects.all(),
        conjoined=False
    )
    
    # Text search
    search = filters.CharFilter(method='filter_search')
    
    # Exclude filters
    exclude_zeros = filters.BooleanFilter(method='filter_exclude_zeros')
    
    class Meta:
        model = KilimoSTATData
        fields = {
            'area': ['exact', 'in'],
            'area__level': ['exact'],
            'source': ['exact'],
            'provider': ['exact'],
            'sector': ['exact'],
            'subsector': ['exact'],
            'indicator': ['exact'],
            'indicator__is_core_indicator': ['exact'],
            'item': ['exact'],
            'item__category': ['exact'],
            'domain': ['exact'],
            'unit': ['exact'],
            'subgroup_dimension': ['exact'],
            'subgroup': ['exact'],
            'time_period': ['exact', 'icontains'],
            'flag': ['exact'],
            'is_active': ['exact'],
            'created_by': ['exact'],
        }
    
    def filter_year_min(self, queryset, name, value):
        """Filter records with time_period >= value"""
        return queryset.filter(time_period__gte=value)
    
    def filter_year_max(self, queryset, name, value):
        """Filter records with time_period <= value"""
        return queryset.filter(time_period__lte=value)
    
    def filter_search(self, queryset, name, value):
        """Search across multiple fields"""
        return queryset.filter(
            Q(area__name__icontains=value) |
            Q(indicator__name__icontains=value) |
            Q(item__name__icontains=value) |
            Q(notes__icontains=value)
        )
    
    def filter_exclude_zeros(self, queryset, name, value):
        """Exclude zero values if True"""
        if value:
            return queryset.exclude(data_value=0)
        return queryset


class IndicatorFilter(filters.FilterSet):
    """
    Filters for Indicator model
    """
    search = filters.CharFilter(method='filter_search')
    
    class Meta:
        model = Indicator
        fields = {
            'name': ['icontains'],
            'is_core_indicator': ['exact'],
            'is_active': ['exact'],
        }
    
    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value) |
            Q(code__icontains=value) |
            Q(description__icontains=value)
        )


class AreaFilter(filters.FilterSet):
    """
    Filters for Area model
    """
    class Meta:
        model = Area
        fields = {
            'name': ['icontains', 'exact'],
            'level': ['exact'],
            'parent': ['exact', 'isnull'],
            'is_active': ['exact'],
        }