# core/signals.py
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils.text import slugify
from .models import KilimoSTATData, Indicator, IndicatorMetadata

@receiver(pre_save, sender=KilimoSTATData)
def generate_slug(sender, instance, **kwargs):
    """Generate slug before saving if not provided"""
    if not instance.slug:
        base_string = f"{instance.area.name}-{instance.indicator.name}-{instance.time_period}"
        if instance.item:
            base_string += f"-{instance.item.name}"
        instance.slug = slugify(base_string)[:500]


@receiver(post_save, sender=Indicator)
def create_indicator_metadata(sender, instance, created, **kwargs):
    """Create indicator metadata when indicator is created"""
    if created:
        IndicatorMetadata.objects.get_or_create(
            indicator=instance,
            defaults={
                'slug': slugify(instance.name)[:500],
            }
        )


@receiver(post_save, sender=KilimoSTATData)
def create_data_metadata(sender, instance, created, **kwargs):
    """Create metadata when data record is created"""
    if created:
        from .models import Metadata
        Metadata.objects.get_or_create(
            data_record=instance,
            defaults={
                'record_identifier': instance.slug,
                'created_by': instance.created_by,
            }
        )