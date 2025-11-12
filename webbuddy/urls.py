"""
URL configuration for webbuddy project.
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from rest_framework_simplejwt.views import TokenRefreshView
from .views import ReactAppView
import users.urls

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # API endpoints
    path('api/', include('queries.urls')),  # Queries API
    path('api/', include('projects.urls')),  # Projects API
    path('api/', include(users.urls.api_urlpatterns)),  # Users API (includes login)
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # React app - catch all routes (must be last)
    re_path(r'^.*$', ReactAppView.as_view(), name='react_app'),
]

# Serve static files in development
if settings.DEBUG:
    from django.views.static import serve
    urlpatterns = [
        # Serve assets from frontend/dist
        re_path(r'^assets/(?P<path>.*)$', serve, {
            'document_root': settings.BASE_DIR / 'frontend' / 'dist' / 'assets',
        }),
        re_path(r'^(?P<path>vite\.svg)$', serve, {
            'document_root': settings.BASE_DIR / 'frontend' / 'dist',
        }),
    ] + urlpatterns