"""
URL configuration for lms_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="Digital Lending Platform API",
        default_version='v1',
        description="""
        Digital Lending Platform API Documentation
        
        # Authentication
        * Basic Auth for Transaction API endpoints
        * No authentication required for other endpoints
        
        # Test Data
        Use these customer numbers for testing:
        * 234774784 - Regular customer
        * 318411216 - High-value customer
        * 340397370 - New customer
        * 366585630 - Existing loan customer
        * 397178638 - Rejected customer
        
        # Flow
        1. Register client (one-time setup)
        2. Subscribe customer
        3. Request loan
        4. Check loan status
        5. Get transaction data
        """,
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="lucasowino14@gmail.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),    
    path('api/v1/', include('loan_management.urls')),
    # Swagger URLs
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', 
            schema_view.without_ui(cache_timeout=0), 
            name='schema-json'),
    path('swagger/', 
         schema_view.with_ui('swagger', cache_timeout=0), 
         name='schema-swagger-ui'),
    path('redoc/', 
         schema_view.with_ui('redoc', cache_timeout=0), 
         name='schema-redoc'),
]
