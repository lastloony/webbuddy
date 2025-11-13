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
        Сервисные аккаунты и администраторы видят все запросы
        """
        user = self.request.user
        if user.has_cross_project_access():
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

    def destroy(self, request, *args, **kwargs):
        """
        Удаление запроса (только если это запрос пользователя из его проекта)
        Можно удалять только запросы в статусах 'done' или 'failed'
        """
        instance = self.get_object()

        # Проверка прав: пользователь должен быть из того же проекта (или иметь cross-project доступ)
        if not request.user.has_cross_project_access() and instance.project_id != request.user.project_id:
            return Response(
                {"detail": "У вас нет прав для удаления этого запроса"},
                status=status.HTTP_403_FORBIDDEN
            )

        # Проверка статуса: можно удалять только завершенные или ошибочные запросы
        if instance.status not in ['done', 'failed']:
            return Response(
                {"detail": f"Нельзя удалить запрос в статусе '{instance.status}'. Можно удалять только запросы в статусах 'done' или 'failed'"},
                status=status.HTTP_400_BAD_REQUEST
            )

        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

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
        Сервисные аккаунты и администраторы видят все логи
        """
        user = self.request.user
        if user.has_cross_project_access():
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
        Сервисные аккаунты и администраторы видят все логи
        """
        user = self.request.user
        if user.has_cross_project_access():
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