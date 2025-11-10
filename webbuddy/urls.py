"""
URL configuration for webbuddy project.
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenRefreshView
from .views import ReactAppView

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # API endpoints
    path('api/', include('queries.urls')),  # Queries API
    path('api/', include('users.urls')),    # Users API (includes login)
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # React app - catch all routes (must be last)
    re_path(r'^.*$', ReactAppView.as_view(), name='react_app'),
]

# Serve static files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)