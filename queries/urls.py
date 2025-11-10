from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import QueryViewSet, QueryLogViewSet, TokenUsageLogViewSet

router = DefaultRouter()
router.register(r'queries', QueryViewSet, basename='query')
router.register(r'logs', QueryLogViewSet, basename='querylog')
router.register(r'token-usage', TokenUsageLogViewSet, basename='tokenusage')

urlpatterns = [
    path('', include(router.urls)),
]