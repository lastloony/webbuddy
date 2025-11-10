"""
URL configuration for webbuddy project.
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # Redirect root to login
    path('', RedirectView.as_view(pattern_name='login', permanent=False)),

    # Users app (auth + user management)
    path('', include('users.urls')),

    # Queries app
    path('', include('queries.urls_web')),  # Web views
    path('api/', include('queries.urls')),  # API views

    # JWT Token endpoints
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]