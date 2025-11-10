from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, api_login, login_view, logout_view, change_password_view

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    # Web URLs
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('change-password/', change_password_view, name='change_password'),

    # API URLs
    path('api/', include(router.urls)),
    path('api/login/', api_login, name='api_login'),
]