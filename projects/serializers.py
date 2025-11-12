from rest_framework import serializers
from .models import Project


class ProjectSerializer(serializers.ModelSerializer):
    """
    Serializer for Project model
    """
    # Add fields to show masked tokens in read mode
    test_it_token_masked = serializers.SerializerMethodField()
    jira_token_masked = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            'id', 'project_name', 'test_it_token', 'test_it_project_id',
            'jira_token', 'jira_project_id', 'project_context',
            'created_at', 'updated_at', 'test_it_token_masked', 'jira_token_masked'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'test_it_token_masked', 'jira_token_masked']
        extra_kwargs = {
            'test_it_token': {'write_only': True, 'required': False, 'allow_blank': True},
            'jira_token': {'write_only': True, 'required': False, 'allow_blank': True},
        }

    def get_test_it_token_masked(self, obj):
        """Return masked TestIt token"""
        if obj.test_it_token:
            return '*' * (len(obj.test_it_token) - 4) + obj.test_it_token[-4:] if len(obj.test_it_token) > 4 else '****'
        return ''

    def get_jira_token_masked(self, obj):
        """Return masked Jira token"""
        if obj.jira_token:
            return '*' * (len(obj.jira_token) - 4) + obj.jira_token[-4:] if len(obj.jira_token) > 4 else '****'
        return ''