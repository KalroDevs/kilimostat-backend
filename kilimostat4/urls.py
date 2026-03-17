from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView


admin.site.site_header = "KilimoSTAT"
admin.site.site_title = "KilimoSTAT" 
admin.site.index_title = "KilimoSTAT - Open data platform from the Ministry of Agriculture and Livestock Development" 

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # API
    path('api/', include('api.urls')),
    
    # Dashboard (if you have one)
    # path('', include('dashboard.urls')),
    
    # Redirect root to API docs in development
    path('', RedirectView.as_view(url='/api/swagger/')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    # Debug toolbar
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns