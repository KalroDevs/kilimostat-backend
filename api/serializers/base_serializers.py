from rest_framework import serializers
from django.utils import timezone

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


class AuditSerializerMixin(serializers.Serializer):
    """
    Mixin to add audit fields to serializers
    """
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    created_by = serializers.CharField(read_only=True)


class TimelineSerializer(serializers.Serializer):
    """
    Serializer for timeline data
    """
    date = serializers.DateField()
    value = serializers.FloatField()
    label = serializers.CharField(required=False)


class GeoJSONSerializer(serializers.Serializer):
    """
    Serializer for GeoJSON output
    """
    type = serializers.CharField(default='FeatureCollection')
    features = serializers.ListField()
    
    def to_representation(self, instance):
        features = []
        for item in instance:
            feature = {
                'type': 'Feature',
                'geometry': {
                    'type': 'Point',
                    'coordinates': [item.area.longitude, item.area.latitude]
                } if item.area.latitude and item.area.longitude else None,
                'properties': {
                    'area_name': item.area.name,
                    'value': item.data_value,
                    'indicator': item.indicator.name,
                    'time_period': item.time_period
                }
            }
            features.append(feature)
        
        return {
            'type': 'FeatureCollection',
            'features': features
        }