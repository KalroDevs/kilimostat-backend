from django.contrib.admin import AdminSite
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin, GroupAdmin

class KilimoSTATAdminSite(AdminSite):
    """Custom Admin Site for KilimoSTAT"""
    
    site_header = "KilimoSTAT Data Management System"
    site_title = "KilimoSTAT Admin Portal"
    index_title = "Welcome to KilimoSTAT Administration"
    
    # Optional: Customize the login template
    login_template = "admin/custom_login.html"
    
    # Optional: Add custom CSS
    def each_context(self, request):
        context = super().each_context(request)
        context['extra_css'] = '/static/css/admin-custom.css'
        return context

# Create an instance of the custom admin site
admin_site = KilimoSTATAdminSite(name='kilimostat_admin')

# Register your models with the custom admin site
from core.models import (
    Area, DataProvider, Source, Sector, Subsector, Indicator,
    ItemCategory, Item, Domain, Unit, SubgroupDimension, Subgroup,
    ProviderContact, ProviderDataset, KilimoSTATData, IndicatorMetadata,
    Frequency, License, Metadata, MetadataChangeLog
)

# Register your models
admin_site.register(Area)
admin_site.register(DataProvider)
admin_site.register(Source)
admin_site.register(Sector)
admin_site.register(Subsector)
admin_site.register(Indicator)
admin_site.register(ItemCategory)
admin_site.register(Item)
admin_site.register(Domain)
admin_site.register(Unit)
admin_site.register(SubgroupDimension)
admin_site.register(Subgroup)
admin_site.register(ProviderContact)
admin_site.register(ProviderDataset)
admin_site.register(KilimoSTATData)
admin_site.register(IndicatorMetadata)
admin_site.register(Frequency)
admin_site.register(License)
admin_site.register(Metadata)
admin_site.register(MetadataChangeLog)

# Register auth models
admin_site.register(User, UserAdmin)
admin_site.register(Group, GroupAdmin)