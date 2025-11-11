from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Count
from .models import Query, QueryLog, TokenUsageLog
from .serializers import (
    QuerySerializer, QueryCreateSerializer, QueryDetailSerializer,
    QueryLogSerializer, TokenUsageLogSerializer, TokenUsageStatsSerializer
)


# ============ Web Views ============

@login_required
def query_create_view(request):
    """
    View for creating a new query
    """
    if request.method == 'POST':
        query_text = request.POST.get('query_text')

        if not query_text:
            messages.error(request, 'Query text is required.')
            return render(request, 'queries/create.html')

        query = Query.objects.create(
            project=request.user.project,
            user=request.user,
            query_text=query_text,
            status='queued'
        )

        messages.success(request, f'Query #{query.id} created successfully.')
        return redirect('query_detail', pk=query.id)

    return render(request, 'queries/create.html')


@login_required
def query_detail_view(request, pk):
    """
    View for displaying query details with logs
    """
    query = get_object_or_404(
        Query.objects.filter(project=request.user.project),
        pk=pk
    )

    return render(request, 'queries/detail.html', {'query': query})


@login_required
def query_list_view(request):
    """
    View for displaying query history
    """
    queries = Query.objects.filter(project=request.user.project).order_by('-query_created')

    return render(request, 'queries/history.html', {'queries': queries})


@login_required
def query_logs_ajax(request, pk):
    """
    AJAX endpoint for getting query logs
    """
    query = get_object_or_404(
        Query.objects.filter(project=request.user.project),
        pk=pk
    )

    logs = query.logs.all().values('id', 'log_data', 'create_dtime')

    return JsonResponse({
        'status': query.status,
        'answer_text': query.answer_text,
        'query_finished': query.query_finished.isoformat() if query.query_finished else None,
        'logs': list(logs)
    })


# ============ API Views ============


class QueryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Query model
    Provides CRUD operations and additional actions for queries
    """
    queryset = Query.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return QueryCreateSerializer
        elif self.action == 'retrieve':
            return QueryDetailSerializer
        return QuerySerializer

    def get_queryset(self):
        """
        Filter queries by user's project
        """
        user = self.request.user
        if user.is_superuser:
            return Query.objects.all()
        return Query.objects.filter(project=user.project)

    def perform_create(self, serializer):
        """
        Create query with current user
        """
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        """
        Override create to return full query data
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        # Return full query data with id
        instance = serializer.instance
        output_serializer = QuerySerializer(instance)
        headers = self.get_success_headers(output_serializer.data)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=True, methods=['get'])
    def logs(self, request, pk=None):
        """
        Get logs for a specific query with pagination
        """
        query = self.get_object()
        logs = query.logs.all()

        page = self.paginate_queryset(logs)
        if page is not None:
            serializer = QueryLogSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = QueryLogSerializer(logs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_status(self, request):
        """
        Get queries filtered by status
        """
        status_filter = request.query_params.get('status', None)
        queryset = self.get_queryset()

        if status_filter:
            queryset = queryset.filter(status=status_filter)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class QueryLogViewSet(viewsets.ModelViewSet):
    """
    ViewSet for QueryLog model
    Allows external service to create logs
    """
    queryset = QueryLog.objects.all()
    serializer_class = QueryLogSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Filter logs by user's project
        """
        user = self.request.user
        if user.is_superuser:
            return QueryLog.objects.all()
        return QueryLog.objects.filter(project=user.project)


class TokenUsageLogViewSet(viewsets.ModelViewSet):
    """
    ViewSet for TokenUsageLog model
    """
    queryset = TokenUsageLog.objects.all()
    serializer_class = TokenUsageLogSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Filter token logs by user's project
        """
        user = self.request.user
        if user.is_superuser:
            return TokenUsageLog.objects.all()
        return TokenUsageLog.objects.filter(project=user.project)

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        Get token usage statistics
        """
        queryset = self.get_queryset()

        # Filter by query_id if provided
        query_id = request.query_params.get('query_id', None)
        if query_id:
            queryset = queryset.filter(query_id=query_id)

        # Calculate statistics
        stats = queryset.aggregate(
            total_tokens=Sum('total_tokens'),
            total_requests=Count('id')
        )

        # Group by agent
        by_agent = queryset.values('ai_agent_name').annotate(
            total=Sum('total_tokens'),
            count=Count('id')
        )

        # Group by model
        by_model = queryset.values('model_name').annotate(
            total=Sum('total_tokens'),
            count=Count('id')
        )

        stats['by_agent'] = {item['ai_agent_name']: item for item in by_agent}
        stats['by_model'] = {item['model_name']: item for item in by_model}

        serializer = TokenUsageStatsSerializer(stats)
        return Response(serializer.data)