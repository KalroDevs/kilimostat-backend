from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator, EmailValidator
from django.utils.text import slugify
from django.utils import timezone
import uuid
import json

from mptt.models import MPTTModel, TreeForeignKey


class Domain(models.Model):    
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=50, unique=True, default='')
    description = models.TextField(blank=True, default='')
    
    class Meta:
        db_table = 'domains'
        verbose_name = 'Domain'
        verbose_name_plural = 'Domains'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if self.code is None:
            self.code = ''
        if self.description is None:
            self.description = ''
        super().save(*args, **kwargs)


class Area(MPTTModel):
    """Lookup table for geographic areas with tree structure"""
    LEVEL_CHOICES = [
        ('COUNTRY', 'Kenya'),
        ('ADMIN_1', 'County'),
        ('ADMIN_2', 'Sub-County'),
        ('ADMIN_3', 'Ward'),
    ]
    
    name = models.CharField(max_length=200, db_index=True)
    administrative_level = models.CharField(
        max_length=50, 
        choices=LEVEL_CHOICES, 
        db_index=True,
        default='ADMIN_1',
        verbose_name="Administrative Level"
    )
    code = models.CharField(max_length=50, blank=True, default='')
    parent = TreeForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='children',
        db_index=True
    )
    latitude = models.FloatField(null=True, blank=True, default=None)
    longitude = models.FloatField(null=True, blank=True, default=None)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class MPTTMeta:
        order_insertion_by = ['name']
        parent_attr = 'parent'
    
    class Meta:
        db_table = 'areas'
        verbose_name = 'Area'
        verbose_name_plural = 'Areas'
        ordering = ['name']
        unique_together = ['name', 'administrative_level']
        indexes = [
            models.Index(fields=['name', 'administrative_level']),
            models.Index(fields=['parent']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.get_administrative_level_display()})"
    
    def get_ancestors_names(self):
        """Get names of all ancestors"""
        return ' > '.join([a.name for a in self.get_ancestors()])
    
    def get_children_count(self):
        """Get count of direct children"""
        return self.get_children().count()
    
    def save(self, *args, **kwargs):
        if self.code is None:
            self.code = ''
        super().save(*args, **kwargs)


class DataProvider(models.Model):
    """
    Lookup table for organizations/institutions that provide the data
    """
    PROVIDER_TYPE_CHOICES = [
        ('government_ministry', 'Government Ministry'),
        ('government_agency', 'Government Agency'),
        ('national_bureau', 'National Statistics Bureau'),
        ('international_organization', 'International Organization'),
        ('research_institute', 'Research Institute'),
        ('university', 'University'),
        ('ngo', 'Non-Governmental Organization'),
        ('private_company', 'Private Company'),
        ('farmer_association', 'Farmer Association'),
        ('industry_body', 'Industry Body'),
        ('individual', 'Individual Researcher'),
        ('other', 'Other'),
    ]
    
    DATA_ACCESS_POLICY_CHOICES = [
        ('open', 'Open Access'),
        ('restricted', 'Restricted Access'),
        ('upon_request', 'Available Upon Request'),
        ('paid', 'Paid/Subscription'),
    ]
    
    # Basic Information
    name = models.CharField(max_length=300, unique=True, db_index=True)
    abbreviation = models.CharField(max_length=50, unique=True, help_text="Short code/abbreviation for the provider")
    provider_type = models.CharField(max_length=50, choices=PROVIDER_TYPE_CHOICES, default='government_agency')
    
    # Contact Information
    contact_person = models.CharField(max_length=200, blank=True, default='')
    email = models.EmailField(blank=True, validators=[EmailValidator()], default='')
    phone = models.CharField(max_length=50, blank=True, default='')
    website = models.URLField(blank=True, default='')
    physical_address = models.TextField(blank=True, default='')
    
    # Organization Details
    headquarters_location = models.CharField(max_length=200, blank=True, default='')
    year_established = models.IntegerField(null=True, blank=True, default=None)
    mandate = models.TextField(blank=True, default='', help_text="Organization's mandate or mission")
    description = models.TextField(blank=True, default='')
    
    # Data Collection Methodology
    data_collection_methods = models.TextField(blank=True, default='', help_text="Standard methods used for data collection")
    sampling_framework = models.TextField(blank=True, default='', help_text="Description of sampling methodology")
    data_frequency = models.CharField(max_length=100, blank=True, default='', help_text="e.g., Annual, Quarterly, Monthly")
    
    # Quality Assurance
    has_quality_certification = models.BooleanField(default=False)
    quality_certification_details = models.TextField(blank=True, default='')
    qa_procedures = models.TextField(blank=True, default='', help_text="Quality assurance procedures followed")
    
    # Partnership/Collaboration
    collaborating_institutions = models.TextField(blank=True, default='', help_text="Other institutions involved in data collection")
    funding_sources = models.TextField(blank=True, default='')
    
    # Data Access
    data_access_policy = models.CharField(
        max_length=50, 
        blank=True, 
        choices=DATA_ACCESS_POLICY_CHOICES, 
        default='open'
    )
    data_license = models.CharField(max_length=200, blank=True, default='', help_text="License type (e.g., CC BY 4.0)")
    citation_recommendation = models.TextField(blank=True, default='', help_text="How to cite this provider's data")
    
    # Metadata
    logo = models.ImageField(upload_to='provider_logos/', null=True, blank=True)
    notes = models.TextField(blank=True, default='')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'data_providers'
        verbose_name = 'Data Provider'
        verbose_name_plural = 'Data Providers'
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['provider_type']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.get_provider_type_display()})"
    
    def contact_count(self):
        return self.contacts.count()
    contact_count.short_description = 'Number of Contacts'
    
    def dataset_count(self):
        return self.datasets.count()
    dataset_count.short_description = 'Number of Datasets'
    
    def save(self, *args, **kwargs):
        # Ensure string fields are not None
        string_fields = ['contact_person', 'email', 'phone', 'website', 'physical_address',
                        'headquarters_location', 'mandate', 'description', 'data_collection_methods',
                        'sampling_framework', 'data_frequency', 'quality_certification_details',
                        'qa_procedures', 'collaborating_institutions', 'funding_sources',
                        'data_license', 'citation_recommendation', 'notes']
        for field in string_fields:
            if getattr(self, field) is None:
                setattr(self, field, '')
        super().save(*args, **kwargs)


class Source(models.Model):
    """Lookup table for data sources"""
    SOURCE_TYPE_CHOICES = [
        ('survey', 'Survey'),
        ('census', 'Census'),
        ('administrative', 'Administrative Data'),
        ('remote_sensing', 'Remote Sensing'),
        ('modeled', 'Modeled Estimates'),
        ('literature', 'Literature Review'),
        ('other', 'Other'),
    ]
    
    name = models.CharField(max_length=500, unique=True, db_index=True)
    code = models.CharField(max_length=100, blank=True, default='')
    provider = models.ForeignKey(DataProvider, on_delete=models.PROTECT, related_name='sources')
    source_type = models.CharField(max_length=50, choices=SOURCE_TYPE_CHOICES, default='survey')
    publication_year = models.IntegerField(null=True, blank=True, default=None)
    access_url = models.URLField(blank=True, default='')
    is_public = models.BooleanField(default=True)
    description = models.TextField(blank=True, default='')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'sources'
        verbose_name = 'Data Source'
        verbose_name_plural = 'Data Sources'
        ordering = ['-publication_year', 'name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['provider']),
            models.Index(fields=['source_type']),
            models.Index(fields=['publication_year']),
        ]
    
    def __str__(self):
        year = f" ({self.publication_year})" if self.publication_year else ""
        return f"{self.name}{year}"
    
    def save(self, *args, **kwargs):
        # Ensure string fields are not None
        if self.code is None:
            self.code = ''
        if self.access_url is None:
            self.access_url = ''
        if self.description is None:
            self.description = ''
        super().save(*args, **kwargs)


class Sector(models.Model):     
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=50, unique=True, default='')
    description = models.TextField(blank=True, default='')
    display_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'sectors'
        verbose_name = 'Sector'
        verbose_name_plural = 'Sectors'
        ordering = ['display_order', 'name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if self.description is None:
            self.description = ''
        super().save(*args, **kwargs)


class Subsector(models.Model):
    """Lookup table for subsectors"""
    sector = models.ForeignKey(Sector, on_delete=models.PROTECT, related_name='subsectors')
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50, unique=True, default='')
    description = models.TextField(blank=True, default='')
    display_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'subsectors'
        verbose_name = 'Subsector'
        verbose_name_plural = 'Subsectors'
        ordering = ['sector', 'display_order', 'name']
        unique_together = ['sector', 'name']
        indexes = [
            models.Index(fields=['sector', 'name']),
        ]
    
    def __str__(self):
        return f"{self.sector.name} - {self.name}"
    
    def save(self, *args, **kwargs):
        if self.description is None:
            self.description = ''
        super().save(*args, **kwargs)


class SubgroupDimension(models.Model):   
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=50, unique=True, default='')
    description = models.TextField(blank=True, default='')
    
    class Meta:
        db_table = 'subgroup_dimensions'
        verbose_name = 'Subgroup Dimension'
        verbose_name_plural = 'Subgroup Dimensions'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if self.code is None:
            self.code = ''
        if self.description is None:
            self.description = ''
        super().save(*args, **kwargs)


class Subgroup(models.Model):
    """Lookup table for subgroups"""
    dimension = models.ForeignKey(SubgroupDimension, on_delete=models.PROTECT, related_name='subgroups')
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50, blank=True, default='')
    description = models.TextField(blank=True, default='')
    
    class Meta:
        db_table = 'subgroups'
        verbose_name = 'Subgroup'
        verbose_name_plural = 'Subgroups'
        ordering = ['dimension', 'name']
        unique_together = ['dimension', 'name']
        indexes = [
            models.Index(fields=['dimension', 'name']),
        ]
    
    def __str__(self):
        return f"{self.dimension.name}: {self.name}"
    
    def save(self, *args, **kwargs):
        if self.description is None:
            self.description = ''
        # Ensure code is not None for unique constraint
        if self.code is None:
            self.code = ''
        super().save(*args, **kwargs)


class Unit(models.Model):
    """Lookup table for units of measurement"""
    UNIT_CATEGORY_CHOICES = [
        ('weight', 'Weight'),
        ('volume', 'Volume'),
        ('area', 'Area'),
        ('count', 'Count'),
        ('rate', 'Rate'),
        ('percentage', 'Percentage'),
        ('currency', 'Currency'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    symbol = models.CharField(max_length=20, blank=True, default='')
    category = models.CharField(max_length=50, choices=UNIT_CATEGORY_CHOICES, default='count')
    description = models.TextField(blank=True, default='')
    
    class Meta:
        db_table = 'units'
        verbose_name = 'Unit'
        verbose_name_plural = 'Units'
        ordering = ['category', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.symbol})" if self.symbol else self.name
    
    def save(self, *args, **kwargs):
        if self.symbol is None:
            self.symbol = ''
        if self.description is None:
            self.description = ''
        super().save(*args, **kwargs)


class Indicator(models.Model):  
    name = models.CharField(max_length=500, unique=True, db_index=True)
    code = models.CharField(max_length=100, blank=True, default='')   
    
    domain = models.ForeignKey(
        Domain, 
        on_delete=models.PROTECT, 
        related_name='indicators',
        help_text="The domain this indicator belongs to",
        null=True,
        blank=True
    )

    subsector = models.ForeignKey(
        Subsector, 
        on_delete=models.PROTECT, 
        related_name='indicators',
        help_text="The subsector this indicator belongs to",
        null=True,
        blank=True
    )
    
    subgroup = models.ForeignKey(
        Subgroup, 
        on_delete=models.PROTECT, 
        related_name='indicators',
        help_text="The subgroup this indicator belongs to",
        null=True,
        blank=True
    )
    
    unit = models.ForeignKey(
        Unit, 
        on_delete=models.PROTECT, 
        related_name='indicators',
        help_text="The unit for the indicator",
        null=True,
        blank=True
    )
    
    description = models.TextField(blank=True, default='')
    is_core_indicator = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'indicators'
        verbose_name = 'Indicator'
        verbose_name_plural = 'Indicators'
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['domain']),
            models.Index(fields=['subsector']),
            models.Index(fields=['subgroup']),
            models.Index(fields=['unit']),  # Fixed: changed from 'unit_of_measure' to 'unit'
        ]
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        # Ensure string fields are not None
        string_fields = ['code', 'description']
        for field in string_fields:
            if getattr(self, field) is None:
                setattr(self, field, '')
        super().save(*args, **kwargs)


class ItemCategory(models.Model):
    """Category for indicator items"""
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=50, unique=True, default='')
    description = models.TextField(blank=True, default='')
    display_order = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'item_categories'
        verbose_name = 'Item Category'
        verbose_name_plural = 'Item Categories'
        ordering = ['display_order', 'name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if self.code is None:
            self.code = ''
        if self.description is None:
            self.description = ''
        super().save(*args, **kwargs)


class Item(models.Model): 
    category = models.ForeignKey(
        ItemCategory, 
        on_delete=models.PROTECT, 
        related_name='items',
        null=True,
        blank=True
    )
    name = models.CharField(max_length=300, db_index=True)
    code = models.CharField(max_length=50, unique=True, default='')
    description = models.TextField(blank=True, default='')
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'items'
        verbose_name = 'Indicator Item'
        verbose_name_plural = 'Indicator Items'
        ordering = ['category__name', 'name']
        unique_together = ['name', 'category']
        indexes = [
            models.Index(fields=['name', 'category']),
        ]
    
    def __str__(self):
        if self.category:
            return f"{self.name} ({self.category.name})"
        return self.name
    
    def save(self, *args, **kwargs):
        if self.code is None:
            self.code = ''
        if self.description is None:
            self.description = ''
        super().save(*args, **kwargs)


# ============================================================================
# PROVIDER CONTACT MODELS
# ============================================================================

class ProviderContact(models.Model):
    """
    Additional contacts for data providers
    """
    provider = models.ForeignKey(
        DataProvider, 
        on_delete=models.CASCADE, 
        related_name='contacts'
    )
    name = models.CharField(max_length=200)
    position = models.CharField(max_length=200, blank=True, default='')
    email = models.EmailField(validators=[EmailValidator()])
    phone = models.CharField(max_length=50, blank=True, default='')
    is_primary = models.BooleanField(default=False)
    notes = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'provider_contacts'
        verbose_name = 'Provider Contact'
        verbose_name_plural = 'Provider Contacts'
        ordering = ['-is_primary', 'name']
        indexes = [
            models.Index(fields=['provider', 'is_primary']),
            models.Index(fields=['email']),
        ]

    def __str__(self):
        return f"{self.name} - {self.provider.name}"

    def save(self, *args, **kwargs):
        from django.db import transaction
        
        with transaction.atomic():
            # If this contact is set as primary, ensure other contacts for this provider are not primary
            if self.is_primary:
                ProviderContact.objects.filter(
                    provider=self.provider, 
                    is_primary=True
                ).exclude(pk=self.pk).update(is_primary=False)
            
            # Ensure string fields are not None
            string_fields = ['position', 'phone', 'notes']
            for field in string_fields:
                if getattr(self, field) is None:
                    setattr(self, field, '')
            
            super().save(*args, **kwargs)


class ProviderDataset(models.Model):
    """
    Datasets published by providers
    """
    provider = models.ForeignKey(
        DataProvider, 
        on_delete=models.CASCADE, 
        related_name='datasets'
    )
    name = models.CharField(max_length=500)
    description = models.TextField(blank=True, default='')
    release_date = models.DateField()
    last_update = models.DateField(null=True, blank=True, default=None)
    version = models.CharField(max_length=50, blank=True, default='')
    methodology = models.TextField(blank=True, default='')
    geographic_coverage = models.TextField(blank=True, default='')
    temporal_coverage = models.CharField(
        max_length=200, 
        blank=True, 
        default='',
        help_text="e.g., 2010-2023"
    )
    url = models.URLField(blank=True, default='', help_text="Link to the dataset")
    citation = models.TextField(blank=True, default='')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'provider_datasets'
        verbose_name = 'Provider Dataset'
        verbose_name_plural = 'Provider Datasets'
        ordering = ['-release_date', 'name']
        indexes = [
            models.Index(fields=['provider', '-release_date']),
            models.Index(fields=['name']),
        ]

    def __str__(self):
        return f"{self.name} - {self.provider.name}"
    
    def save(self, *args, **kwargs):
        # Ensure string fields are not None
        string_fields = ['description', 'version', 'methodology', 'geographic_coverage', 
                         'temporal_coverage', 'url', 'citation']
        for field in string_fields:
            if getattr(self, field) is None:
                setattr(self, field, '')
        super().save(*args, **kwargs)


# ============================================================================
# MAIN DATA MODEL
# ============================================================================

class KilimoSTATData(models.Model):
    """Main fact table for food systems data"""
    FLAG_CHOICES = [
        ('official', 'Official figure'),
        ('estimated', 'Estimated figure'),
        ('projected', 'Projected'),
        ('preliminary', 'Preliminary'),
        ('revised', 'Revised'),
    ]
    
    # Foreign keys to lookup tables
    area = models.ForeignKey(Area, on_delete=models.PROTECT, related_name='data_records')
    source = models.ForeignKey(Source, on_delete=models.PROTECT, related_name='data_records')
    provider = models.ForeignKey(DataProvider, on_delete=models.PROTECT, related_name='data_records',
                                help_text="Organization that provided the data")
    sector = models.ForeignKey(Sector, on_delete=models.PROTECT, related_name='data_records')
    subsector = models.ForeignKey(Subsector, on_delete=models.PROTECT, related_name='data_records')
    indicator = models.ForeignKey(Indicator, on_delete=models.PROTECT, related_name='data_records')
    item = models.ForeignKey(Item, on_delete=models.PROTECT, related_name='data_records', 
                            null=True, blank=True)
    domain = models.ForeignKey(Domain, on_delete=models.PROTECT, related_name='data_records')
    unit = models.ForeignKey(Unit, on_delete=models.PROTECT, related_name='data_records')
    subgroup_dimension = models.ForeignKey(SubgroupDimension, on_delete=models.PROTECT, 
                                          related_name='data_records', null=True, blank=True)
    subgroup = models.ForeignKey(Subgroup, on_delete=models.PROTECT, related_name='data_records',
                                null=True, blank=True)
    
    # Data fields
    slug = models.SlugField(max_length=500, unique=True, db_index=True)
    time_period = models.CharField(max_length=50, db_index=True)
    data_value = models.FloatField(validators=[MinValueValidator(0)])
    
    flag = models.CharField(max_length=50, choices=FLAG_CHOICES, blank=True, default='')
    
    # Confidence/Quality metrics
    confidence_lower = models.FloatField(null=True, blank=True, default=None)
    confidence_upper = models.FloatField(null=True, blank=True, default=None)
    standard_error = models.FloatField(null=True, blank=True, default=None)
    sample_size = models.IntegerField(null=True, blank=True, default=None)
    
    # Basic metadata
    notes = models.TextField(blank=True, default='')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=100, blank=True, default='')
    
    class Meta:
        db_table = 'kilimostat_data'
        verbose_name = 'KilimoSTAT Data Record'
        verbose_name_plural = 'KilimoSTAT Data Records'
        ordering = ['-time_period', 'area__name']
        indexes = [
            models.Index(fields=['area', 'time_period']),
            models.Index(fields=['sector', 'indicator']),
            models.Index(fields=['source']),
            models.Index(fields=['provider']),
            models.Index(fields=['domain']),
            models.Index(fields=['time_period']),
            models.Index(fields=['slug']),
            models.Index(fields=['indicator', 'area', 'time_period']),
        ]
    
    def __str__(self):
        item_str = f" - {self.item.name}" if self.item else ""
        return f"{self.indicator.name}{item_str} - {self.area.name} ({self.time_period})"
    
    def clean(self):
        from django.core.exceptions import ValidationError
        # Validate that subgroup_dimension and subgroup are both set or both null
        if (self.subgroup_dimension is None) != (self.subgroup is None):
            raise ValidationError("Both subgroup_dimension and subgroup must be set together or both null")
    
    def save(self, *args, **kwargs):
        self.clean()
        
        if not self.slug:
            base_string = f"{self.area.name}-{self.indicator.name}-{self.time_period}"
            if self.item:
                base_string += f"-{self.item.name}"
            self.slug = slugify(base_string)[:500]
        
        # Ensure string fields are not None
        string_fields = ['flag', 'notes', 'created_by']
        for field in string_fields:
            if getattr(self, field) is None:
                setattr(self, field, '')
        
        super().save(*args, **kwargs)
    
    def get_metadata(self):
        """Helper method to get metadata"""
        try:
            return self.metadata
        except Metadata.DoesNotExist:
            return None


# ============================================================================
# METADATA MODELS
# ============================================================================

class IndicatorMetadata(models.Model):
    """
    Standalone metadata for indicators (separate from data point metadata)
    """
    # Basic identification
    slug = models.SlugField(max_length=500, unique=True, db_index=True)
    indicator = models.OneToOneField(Indicator, on_delete=models.CASCADE, related_name='metadata')
    sector = models.ForeignKey(Sector, on_delete=models.PROTECT, null=True, blank=True)
    sub_sector = models.ForeignKey(Subsector, on_delete=models.PROTECT, null=True, blank=True)
    unit = models.ForeignKey(Unit, on_delete=models.PROTECT, null=True, blank=True)
    
    # Definition and context
    definition = models.TextField(blank=True, default='')
    relevance = models.TextField(blank=True, default='')
    
    # Methodology
    calculation = models.TextField(blank=True, default='')
    treatment_of_missing_values = models.TextField(blank=True, default='')
    
    # Disaggregation
    disaggregation = models.TextField(blank=True, default='')
    
    # Source
    source_hyperlink = models.URLField(blank=True, default='')
    source_description = models.TextField(blank=True, default='')
    
    # Additional metadata
    data_provider = models.ForeignKey(
        DataProvider, 
        on_delete=models.PROTECT, 
        null=True, 
        blank=True, 
        related_name='indicator_metadata'
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'indicator_metadata'
        verbose_name = 'Indicator Metadata'
        verbose_name_plural = 'Indicator Metadata'
        indexes = [
            models.Index(fields=['sector', 'sub_sector']),
        ]
    
    def __str__(self):
        return f"Metadata for {self.indicator.name}"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.indicator.name)[:500]
        
        # Ensure string fields are not None
        string_fields = ['definition', 'relevance', 'calculation', 'treatment_of_missing_values',
                         'disaggregation', 'source_hyperlink', 'source_description']
        for field in string_fields:
            if getattr(self, field) is None:
                setattr(self, field, '')
        
        super().save(*args, **kwargs)


class Frequency(models.Model):
    """Lookup table for data frequencies"""
    name = models.CharField(max_length=50, unique=True)
    code = models.CharField(max_length=20, unique=True, default='')
    description = models.TextField(blank=True, default='')
    
    class Meta:
        db_table = 'frequencies'
        verbose_name = 'Frequency'
        verbose_name_plural = 'Frequencies'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if self.code is None:
            self.code = ''
        if self.description is None:
            self.description = ''
        super().save(*args, **kwargs)


class License(models.Model):
    """Lookup table for licenses"""
    LICENSE_TYPE_CHOICES = [
        ('cc_by', 'CC BY'),
        ('cc_by_sa', 'CC BY-SA'),
        ('cc_by_nc', 'CC BY-NC'),
        ('cc_by_nd', 'CC BY-ND'),
        ('cc_by_nc_sa', 'CC BY-NC-SA'),
        ('cc_by_nc_nd', 'CC BY-NC-ND'),
        ('cc0', 'CC0'),
        ('other_open', 'Other Open License'),
        ('proprietary', 'Proprietary'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, choices=LICENSE_TYPE_CHOICES, unique=True, default='cc_by')
    url = models.URLField(blank=True, default='')
    description = models.TextField(blank=True, default='')
    
    class Meta:
        db_table = 'licenses'
        verbose_name = 'License'
        verbose_name_plural = 'Licenses'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if self.url is None:
            self.url = ''
        if self.description is None:
            self.description = ''
        super().save(*args, **kwargs)


class Metadata(models.Model):
    """
    Comprehensive metadata table for tracking all aspects of data lineage,
    quality, processing, and governance.
    """
    PROVENANCE_LEVEL_CHOICES = [
        ('primary', 'Primary Data'),
        ('secondary', 'Secondary Data'),
        ('derived', 'Derived Data'),
    ]
    
    QUALITY_SCORE_CATEGORY = [
        ('excellent', 'Excellent'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('poor', 'Poor'),
        ('unassessed', 'Not Assessed'),
    ]
    
    METHOD_TYPE_CHOICES = [
        ('census', 'Complete Census'),
        ('sample_survey', 'Sample Survey'),
        ('administrative', 'Administrative Data'),
        ('model_estimation', 'Model-based Estimation'),
    ]
    
    TIME_TYPE_CHOICES = [
        ('point', 'Point in time'),
        ('period', 'Time period'),
    ]
    
    GEOGRAPHIC_LEVEL_CHOICES = [
        ('global', 'Global'),
        ('regional', 'Regional'),
        ('national', 'National'),
        ('subnational', 'Sub-national'),
        ('local', 'Local'),
    ]
    
    ACCESS_LEVEL_CHOICES = [
        ('public', 'Public Access'),
        ('restricted', 'Restricted Access'),
        ('internal', 'Internal Use Only'),
    ]
    
    REVIEW_STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending_review', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    # Link to main data record
    data_record = models.OneToOneField(
        KilimoSTATData, 
        on_delete=models.CASCADE, 
        related_name='metadata',
        primary_key=True
    )
    
    # =========================================================================
    # SECTION 1: BASIC METADATA
    # =========================================================================
    metadata_version = models.CharField(
        max_length=10, 
        default='2.0',
        help_text="Version of metadata schema"
    )
    
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    record_identifier = models.CharField(max_length=200, unique=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True, default=None)
    embargo_until = models.DateTimeField(null=True, blank=True, default=None)
    
    # =========================================================================
    # SECTION 2: INDICATOR METADATA (Reference to IndicatorMetadata)
    # =========================================================================
    indicator_metadata = models.ForeignKey(
        IndicatorMetadata, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='data_metadata'
    )
    
    # =========================================================================
    # SECTION 3: DATA PROVENANCE & LINEAGE
    # =========================================================================
    provenance_level = models.CharField(max_length=20, choices=PROVENANCE_LEVEL_CHOICES, default='primary')
    
    original_source_name = models.CharField(max_length=500, blank=True, default='')
    original_source_url = models.URLField(blank=True, default='')
    original_source_id = models.CharField(max_length=200, blank=True, default='')
    original_data_location = models.TextField(blank=True, default='')
    
    processing_notes = models.TextField(blank=True, default='')
    derived_from = models.ManyToManyField('self', symmetrical=False, blank=True)
    
    # =========================================================================
    # SECTION 4: DATA QUALITY METRICS
    # =========================================================================
    quality_score = models.FloatField(
        null=True, blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        default=None
    )
    quality_category = models.CharField(
        max_length=20, 
        choices=QUALITY_SCORE_CATEGORY,
        default='unassessed'
    )
    
    completeness = models.FloatField(
        null=True, blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        default=None
    )
    accuracy = models.FloatField(
        null=True, blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        default=None
    )
    consistency = models.FloatField(
        null=True, blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        default=None
    )
    
    quality_notes = models.TextField(blank=True, default='')
    quality_check_date = models.DateField(null=True, blank=True, default=None)
    
    # =========================================================================
    # SECTION 5: METHODOLOGY
    # =========================================================================
    methodology_type = models.CharField(max_length=30, choices=METHOD_TYPE_CHOICES, null=True, blank=True, default=None)
    methodology_description = models.TextField(blank=True, default='')
    methodology_url = models.URLField(blank=True, default='')
    
    sample_size = models.IntegerField(null=True, blank=True, default=None)
    sampling_error = models.FloatField(null=True, blank=True, default=None)
    response_rate = models.FloatField(
        null=True, blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        default=None
    )
    
    # =========================================================================
    # SECTION 6: STATISTICAL PROPERTIES
    # =========================================================================
    mean = models.FloatField(null=True, blank=True, default=None)
    median = models.FloatField(null=True, blank=True, default=None)
    standard_deviation = models.FloatField(null=True, blank=True, default=None)
    range_min = models.FloatField(null=True, blank=True, default=None)
    range_max = models.FloatField(null=True, blank=True, default=None)
    
    confidence_level = models.FloatField(
        null=True, blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        default=None
    )
    confidence_interval_lower = models.FloatField(null=True, blank=True, default=None)
    confidence_interval_upper = models.FloatField(null=True, blank=True, default=None)
    
    # =========================================================================
    # SECTION 7: TEMPORAL INFORMATION
    # =========================================================================
    time_type = models.CharField(max_length=20, choices=TIME_TYPE_CHOICES, default='point')
    
    reference_period_start = models.DateField(null=True, blank=True, default=None)
    reference_period_end = models.DateField(null=True, blank=True, default=None)
    reference_period_description = models.CharField(max_length=200, blank=True, default='')
    
    frequency = models.ForeignKey(
        Frequency,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='metadata_records'
    )
    
    # =========================================================================
    # SECTION 8: GEOGRAPHIC INFORMATION
    # =========================================================================
    geographic_level = models.CharField(max_length=20, choices=GEOGRAPHIC_LEVEL_CHOICES, default='national')
    
    geographic_scope = models.TextField(blank=True, default='')
    spatial_resolution = models.CharField(max_length=100, blank=True, default='')
    
    # =========================================================================
    # SECTION 9: ACCESS & USAGE
    # =========================================================================
    access_level = models.CharField(max_length=20, choices=ACCESS_LEVEL_CHOICES, default='public')
    
    license = models.ForeignKey(
        License,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='metadata_records'
    )
    license_url = models.URLField(blank=True, default='')
    
    citation_recommendation = models.TextField(blank=True, default='')
    
    download_count = models.IntegerField(default=0)
    view_count = models.IntegerField(default=0)
    last_accessed = models.DateTimeField(null=True, blank=True, default=None)
    
    # =========================================================================
    # SECTION 10: REVIEW & VALIDATION
    # =========================================================================
    review_status = models.CharField(max_length=20, choices=REVIEW_STATUS_CHOICES, default='draft')
    
    review_date = models.DateField(null=True, blank=True, default=None)
    reviewed_by = models.CharField(max_length=200, blank=True, default='')
    reviewer_notes = models.TextField(blank=True, default='')
    
    approved_by = models.CharField(max_length=200, blank=True, default='')
    approval_date = models.DateField(null=True, blank=True, default=None)
    
    # =========================================================================
    # SECTION 11: VERSIONING
    # =========================================================================
    version = models.CharField(max_length=20, default='1.0')
    previous_version = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='next_version'
    )
    version_notes = models.TextField(blank=True, default='')
    is_latest_version = models.BooleanField(default=True)
    
    # =========================================================================
    # SECTION 12: CONTACT & RESPONSIBILITY
    # =========================================================================
    data_owner = models.CharField(max_length=200, blank=True, default='')
    contact_email = models.EmailField(blank=True, validators=[EmailValidator()], default='')
    
    # =========================================================================
    # SECTION 13: TAGS & CLASSIFICATIONS
    # =========================================================================
    keywords = models.TextField(blank=True, default='', help_text="Comma-separated keywords")
    sdg_goals = models.CharField(max_length=200, blank=True, default='', help_text="Comma-separated SDG goals")
    is_official_statistic = models.BooleanField(default=False)
    
    # =========================================================================
    # SECTION 14: CUSTOM FIELDS
    # =========================================================================
    custom_metadata = models.JSONField(
        null=True, blank=True, default=None,
        help_text="JSON field for custom metadata"
    )
    
    # =========================================================================
    # SECTION 15: AUDIT INFORMATION
    # =========================================================================
    created_by = models.CharField(max_length=200, blank=True, default='')
    modified_by = models.CharField(max_length=200, blank=True, default='')
    
    class Meta:
        db_table = 'metadata'
        verbose_name = 'Metadata'
        verbose_name_plural = 'Metadata'
        indexes = [
            models.Index(fields=['quality_score']),
            models.Index(fields=['review_status']),
            models.Index(fields=['version', 'is_latest_version']),
            models.Index(fields=['published_at']),
        ]
    
    def __str__(self):
        return f"Metadata for {self.data_record} (v{self.version})"
    
    def save(self, *args, **kwargs):
        # Auto-calculate quality category based on score
        if self.quality_score is not None:
            if self.quality_score >= 90:
                self.quality_category = 'excellent'
            elif self.quality_score >= 75:
                self.quality_category = 'good'
            elif self.quality_score >= 60:
                self.quality_category = 'fair'
            elif self.quality_score < 60:
                self.quality_category = 'poor'
        
        # Auto-set record_identifier if not set
        if not self.record_identifier and hasattr(self, 'data_record') and self.data_record:
            self.record_identifier = self.data_record.slug
        
        # Ensure string fields are not None
        string_fields = ['original_source_name', 'original_source_url', 'original_source_id',
                        'original_data_location', 'processing_notes', 'quality_notes',
                        'methodology_description', 'methodology_url', 'reference_period_description',
                        'geographic_scope', 'spatial_resolution', 'license_url',
                        'citation_recommendation', 'reviewed_by', 'reviewer_notes', 'approved_by',
                        'version_notes', 'data_owner', 'contact_email', 'keywords', 'sdg_goals',
                        'created_by', 'modified_by']
        
        for field in string_fields:
            if hasattr(self, field) and getattr(self, field) is None:
                setattr(self, field, '')
        
        super().save(*args, **kwargs)


class MetadataChangeLog(models.Model):
    """
    Track changes to metadata over time for complete audit trail
    """
    CHANGE_TYPE_CHOICES = [
        ('create', 'Creation'),
        ('update', 'Update'),
        ('delete', 'Deletion'),
        ('review', 'Review Status Change'),
        ('version', 'Version Change'),
    ]
    
    metadata = models.ForeignKey(
        Metadata, 
        on_delete=models.CASCADE, 
        related_name='change_logs'
    )
    changed_at = models.DateTimeField(auto_now_add=True)
    changed_by = models.CharField(max_length=200)
    change_type = models.CharField(max_length=50, choices=CHANGE_TYPE_CHOICES, default='update')
    field_name = models.CharField(max_length=200, blank=True, default='')
    old_value = models.TextField(blank=True, default='')
    new_value = models.TextField(blank=True, default='')
    change_reason = models.TextField(blank=True, default='')

    class Meta:
        db_table = 'metadata_change_log'
        verbose_name = 'Metadata Change Log'
        verbose_name_plural = 'Metadata Change Logs'
        ordering = ['-changed_at']
        indexes = [
            models.Index(fields=['metadata', '-changed_at']),
            models.Index(fields=['changed_by']),
            models.Index(fields=['change_type']),
        ]

    def __str__(self):
        return f"{self.get_change_type_display()} - {self.changed_at}"
    
    def save(self, *args, **kwargs):
        # Ensure string fields are not None
        string_fields = ['field_name', 'old_value', 'new_value', 'change_reason']
        for field in string_fields:
            if getattr(self, field) is None:
                setattr(self, field, '')
        super().save(*args, **kwargs)


# ============================================================================
# SIGNALS
# ============================================================================

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

@receiver(pre_save, sender=KilimoSTATData)
def generate_slug(sender, instance, **kwargs):
    """Generate slug before saving if not provided"""
    if not instance.slug:
        base_string = f"{instance.area.name}-{instance.indicator.name}-{instance.time_period}"
        if instance.item:
            base_string += f"-{instance.item.name}"
        instance.slug = slugify(base_string)[:500]


@receiver(post_save, sender=KilimoSTATData)
def create_metadata(sender, instance, created, **kwargs):
    """Automatically create metadata record when KilimoSTATData is created"""
    if created:
        Metadata.objects.get_or_create(
            data_record=instance,
            defaults={
                'record_identifier': instance.slug,
                'created_by': instance.created_by,
            }
        )


@receiver(post_save, sender=Indicator)
def create_indicator_metadata(sender, instance, created, **kwargs):
    """Automatically create indicator metadata when Indicator is created"""
    if created:
        IndicatorMetadata.objects.get_or_create(
            indicator=instance,
            defaults={
                'slug': slugify(instance.name)[:500],
            }
        )