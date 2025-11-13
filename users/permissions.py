"""
Custom permission classes для управления доступом
"""
from rest_framework import permissions


class IsServiceAccountOrReadOnly(permissions.BasePermission):
    """
    Разрешает доступ на запись только сервисным аккаунтам.
    Остальным пользователям доступ только на чтение.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated and request.user.is_service_account()


class IsServiceAccount(permissions.BasePermission):
    """
    Разрешает доступ только сервисным аккаунтам
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_service_account()


class HasCrossProjectAccess(permissions.BasePermission):
    """
    Разрешает доступ пользователям с правами cross-project (admin, service, superuser)
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.has_cross_project_access()