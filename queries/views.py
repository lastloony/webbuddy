from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db import transaction
from django.utils import timezone
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


# ============ Веб-представления ============

@login_required
def query_create_view(request):
    """
    Представление для создания нового запроса
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
    Представление для отображения деталей запроса с логами
    """
    query = get_object_or_404(
        Query.objects.filter(project=request.user.project),
        pk=pk
    )

    return render(request, 'queries/detail.html', {'query': query})


@login_required
def query_list_view(request):
    """
    Представление для отображения истории запросов
    """
    queries = Query.objects.filter(project=request.user.project).order_by('-query_created')

    return render(request, 'queries/history.html', {'queries': queries})


@login_required
def query_logs_ajax(request, pk):
    """
    AJAX-эндпоинт для получения логов запроса
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


# ============ API-представления ============


class QueryViewSet(viewsets.ModelViewSet):
    """
    ViewSet для модели Query
    Предоставляет CRUD-операции и дополнительные действия для запросов
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
        Фильтрация запросов по проекту пользователя
        """
        user = self.request.user
        if user.is_superuser:
            return Query.objects.all()
        return Query.objects.filter(project=user.project)

    def perform_create(self, serializer):
        """
        Создание запроса с текущим пользователем
        """
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        """
        Переопределение create для возврата полных данных запроса
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        # Возврат полных данных запроса с id
        instance = serializer.instance
        output_serializer = QuerySerializer(instance)
        headers = self.get_success_headers(output_serializer.data)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=True, methods=['get'])
    def logs(self, request, pk=None):
        """
        Получение логов для конкретного запроса с пагинацией
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
        Получение запросов, отфильтрованных по статусу
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

    @action(detail=False, methods=['post'])
    def claim_next(self, request):
        """
        Атомарное получение следующего запроса из очереди для обработки
        Возвращает полученный запрос или 404, если очередь пуста
        """
        with transaction.atomic():
            # Получение первого запроса в очереди с блокировкой на уровне строки
            query = self.get_queryset().select_for_update(skip_locked=True).filter(
                status='queued'
            ).order_by('query_created').first()

            if not query:
                return Response(
                    {'detail': 'No queued queries available'},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Обновление статуса на in_progress
            query.status = 'in_progress'
            query.query_started = timezone.now()
            query.save()

            # Возврат полных данных запроса
            serializer = QuerySerializer(query)
            return Response(serializer.data, status=status.HTTP_200_OK)


class QueryLogViewSet(viewsets.ModelViewSet):
    """
    ViewSet для модели QueryLog
    Позволяет внешнему сервису создавать логи
    """
    queryset = QueryLog.objects.all()
    serializer_class = QueryLogSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Фильтрация логов по проекту пользователя
        """
        user = self.request.user
        if user.is_superuser:
            return QueryLog.objects.all()
        return QueryLog.objects.filter(project=user.project)


class TokenUsageLogViewSet(viewsets.ModelViewSet):
    """
    ViewSet для модели TokenUsageLog
    """
    queryset = TokenUsageLog.objects.all()
    serializer_class = TokenUsageLogSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Фильтрация логов использования токенов по проекту пользователя
        """
        user = self.request.user
        if user.is_superuser:
            return TokenUsageLog.objects.all()
        return TokenUsageLog.objects.filter(project=user.project)

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        Получение статистики использования токенов
        """
        queryset = self.get_queryset()

        # Фильтрация по query_id, если указан
        query_id = request.query_params.get('query_id', None)
        if query_id:
            queryset = queryset.filter(query_id=query_id)

        # Расчет статистики
        stats = queryset.aggregate(
            total_tokens=Sum('total_tokens'),
            total_requests=Count('id')
        )

        # Группировка по агенту
        by_agent = queryset.values('ai_agent_name').annotate(
            total=Sum('total_tokens'),
            count=Count('id')
        )

        # Группировка по модели
        by_model = queryset.values('model_name').annotate(
            total=Sum('total_tokens'),
            count=Count('id')
        )

        stats['by_agent'] = {item['ai_agent_name']: item for item in by_agent}
        stats['by_model'] = {item['model_name']: item for item in by_model}

        serializer = TokenUsageStatsSerializer(stats)
        return Response(serializer.data)