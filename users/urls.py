from django.urls import path, include
from django.views.decorators.csrf import csrf_exempt
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, api_login_view, login_view, logout_view, change_password_view

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

# API URLs (будут префиксированы с 'api/' в главном urls.py)
api_urlpatterns = [
    path('', include(router.urls)),
    path('login/', csrf_exempt(api_login_view), name='api_login'),
]

# Web URLs (без префикса)
web_urlpatterns = [
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('change-password/', change_password_view, name='change_password'),
]

# For compatibility
urlpatterns = api_urlpatterns