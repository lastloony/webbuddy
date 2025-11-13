from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Project
from .serializers import ProjectSerializer


class ProjectViewSet(viewsets.ModelViewSet):
    """
    ViewSet для модели Project с контролем доступа к проекту пользователя
    """
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Пользователи могут видеть только свой проект
        Сервисные аккаунты и администраторы видят все проекты
        """
        user = self.request.user
        if user.has_cross_project_access():
            return Project.objects.all()
        return Project.objects.filter(id=user.project_id)

    @action(detail=False, methods=['get'])
    def my_project(self, request):
        """
        Получение проекта текущего пользователя
        """
        user = request.user
        if not user.project_id:
            return Response(
                {"detail": "User is not assigned to any project"},
                status=status.HTTP_404_NOT_FOUND
            )

        project = Project.objects.get(id=user.project_id)
        serializer = self.get_serializer(project)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def my_project_tokens(self, request):
        """
        Получение проекта текущего пользователя с ПОЛНЫМИ токенами (для Worker Service)
        ВНИМАНИЕ: Возвращает конфиденциальные данные!
        """
        user = request.user
        if not user.project_id:
            return Response(
                {"detail": "User is not assigned to any project"},
                status=status.HTTP_404_NOT_FOUND
            )

        project = Project.objects.get(id=user.project_id)

        # Возврат полных данных, включая токены
        return Response({
            "id": project.id,
            "project_name": project.project_name,
            "test_it_token": project.test_it_token,
            "test_it_project_id": project.test_it_project_id,
            "jira_token": project.jira_token,
            "jira_project_id": project.jira_project_id,
            "project_context": project.project_context,
            "created_at": project.created_at,
            "updated_at": project.updated_at,
        })

    @action(detail=True, methods=['get'], url_path='tokens')
    def get_project_tokens(self, request, pk=None):
        """
        Получение конкретного проекта с ПОЛНЫМИ токенами по ID проекта (для Worker Service)
        ВНИМАНИЕ: Возвращает конфиденциальные данные!
        Пользователь должен быть назначен на этот проект.
        """
        try:
            project = Project.objects.get(id=pk)
        except Project.DoesNotExist:
            return Response(
                {"detail": "Project not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Проверка принадлежности пользователя к этому проекту (или наличия cross-project доступа)
        if not request.user.has_cross_project_access() and request.user.project_id != project.id:
            return Response(
                {"detail": "You don't have permission to access this project"},
                status=status.HTTP_403_FORBIDDEN
            )

        # Возврат полных данных, включая токены
        return Response({
            "id": project.id,
            "project_name": project.project_name,
            "test_it_token": project.test_it_token,
            "test_it_project_id": project.test_it_project_id,
            "jira_token": project.jira_token,
            "jira_project_id": project.jira_project_id,
            "project_context": project.project_context,
            "created_at": project.created_at,
            "updated_at": project.updated_at,
        })

    def update(self, request, *args, **kwargs):
        """
        Обновление проекта (только если это проект пользователя или есть cross-project доступ)
        """
        instance = self.get_object()
        if not request.user.has_cross_project_access() and instance.id != request.user.project_id:
            return Response(
                {"detail": "You don't have permission to edit this project"},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        """
        Частичное обновление проекта (только если это проект пользователя или есть cross-project доступ)
        """
        instance = self.get_object()
        if not request.user.has_cross_project_access() and instance.id != request.user.project_id:
            return Response(
                {"detail": "You don't have permission to edit this project"},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().partial_update(request, *args, **kwargs)