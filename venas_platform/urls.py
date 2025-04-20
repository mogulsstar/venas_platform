"""
URL configuration for venas_platform project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# API documentation schema
schema_view = get_schema_view(
    openapi.Info(
        title="VENAS Platform API",
        default_version='v1',
        description="API documentation for VENAS Autonomous Driving Compliance Platform",
        terms_of_service="https://www.venas.com/terms/",
        contact=openapi.Contact(email="contact@venas.com"),
        license=openapi.License(name="Proprietary License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # Admin site
    path('admin/', admin.site.urls),
    
    # API documentation
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    
    # API endpoints
    path('api/v1/regulations/', include('regulations.urls')),
    path('api/v1/testcases/', include('testcases.urls')),
    path('api/v1/projects/', include('projects.urls')),
    path('api/v1/analysis/', include('analysis.urls')),
    path('api/v1/dashboard/', include('dashboard.urls')),
    path('api/v1/monitor/', include('monitor.urls')),
    path('api/v1/users/', include('users.urls')),
    path('api/v1/help/', include('help_center.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
