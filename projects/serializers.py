from rest_framework import serializers
from .models import Project


class ProjectSerializer(serializers.ModelSerializer):
    """
    Serializer for Project model
    """
    class Meta:
        model = Project
        fields = [
            'id', 'project_name', 'test_it_token', 'test_it_project_id',
            'jira_token', 'jira_project_id', 'project_context',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'test_it_token': {'write_only': True},
            'jira_token': {'write_only': True},
        }