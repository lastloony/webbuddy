"""
URL configuration for webbuddy project.
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from rest_framework_simplejwt.views import TokenRefreshView
from .views import ReactAppView
import users.urls

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # Web URLs (users web views)
    path('', include(users.urls.web_urlpatterns)),

    # API endpoints
    path('api/', include('queries.urls')),  # Queries API
    path('api/', include(users.urls.api_urlpatterns)),    # Users API (includes login)
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # React app - catch all routes (must be last)
    re_path(r'^.*$', ReactAppView.as_view(), name='react_app'),
]

# Serve static files in development
if settings.DEBUG:
    # Serve files from frontend/dist (including assets folder)
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