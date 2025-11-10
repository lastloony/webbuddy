from django.urls import path
from .views import (
    query_create_view,
    query_detail_view,
    query_list_view,
    query_logs_ajax
)

urlpatterns = [
    path('queries/create/', query_create_view, name='query_create'),
    path('queries/<int:pk>/', query_detail_view, name='query_detail'),
    path('queries/', query_list_view, name='query_list'),
    path('queries/<int:pk>/logs/ajax/', query_logs_ajax, name='query_logs_ajax'),
]