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
