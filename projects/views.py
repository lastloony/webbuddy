from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Project
from .serializers import ProjectSerializer


class ProjectViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Project model with user's project access control
    """
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Users can only see their own project
        """
        user = self.request.user
        return Project.objects.filter(id=user.project_id)

    @action(detail=False, methods=['get'])
    def my_project(self, request):
        """
        Get current user's project
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
        Get current user's project with FULL tokens (for Worker Service)
        WARNING: Returns sensitive data!
        """
        user = request.user
        if not user.project_id:
            return Response(
                {"detail": "User is not assigned to any project"},
                status=status.HTTP_404_NOT_FOUND
            )

        project = Project.objects.get(id=user.project_id)

        # Return full data including tokens
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
        Get specific project with FULL tokens by project ID (for Worker Service)
        WARNING: Returns sensitive data!
        User must be assigned to this project.
        """
        try:
            project = Project.objects.get(id=pk)
        except Project.DoesNotExist:
            return Response(
                {"detail": "Project not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Check if user belongs to this project
        if request.user.project_id != project.id:
            return Response(
                {"detail": "You don't have permission to access this project"},
                status=status.HTTP_403_FORBIDDEN
            )

        # Return full data including tokens
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
        Update project (only if it's user's project)
        """
        instance = self.get_object()
        if instance.id != request.user.project_id:
            return Response(
                {"detail": "You don't have permission to edit this project"},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        """
        Partial update project (only if it's user's project)
        """
        instance = self.get_object()
        if instance.id != request.user.project_id:
            return Response(
                {"detail": "You don't have permission to edit this project"},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().partial_update(request, *args, **kwargs)
