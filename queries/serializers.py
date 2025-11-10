from rest_framework import serializers
from .models import Query, QueryLog, TokenUsageLog


class QueryLogSerializer(serializers.ModelSerializer):
    """
    Serializer for QueryLog model
    """
    class Meta:
        model = QueryLog
        fields = ['id', 'project', 'query', 'log_data', 'create_dtime']
        read_only_fields = ['id', 'create_dtime']


class QuerySerializer(serializers.ModelSerializer):
    """
    Serializer for Query model
    """
    user_name = serializers.CharField(source='user.username', read_only=True)
    project_name = serializers.CharField(source='project.project_name', read_only=True)
    logs_count = serializers.SerializerMethodField()

    class Meta:
        model = Query
        fields = [
            'id', 'project', 'project_name', 'user', 'user_name',
            'query_text', 'answer_text', 'status',
            'query_created', 'query_finished', 'logs_count'
        ]
        read_only_fields = ['id', 'query_created', 'query_finished', 'user']

    def get_logs_count(self, obj):
        return obj.logs.count()


class QueryCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating Query
    """
    class Meta:
        model = Query
        fields = ['project', 'query_text']

    def create(self, validated_data):
        # User will be set from request.user in viewset
        return Query.objects.create(**validated_data, status='queued')


class QueryDetailSerializer(QuerySerializer):
    """
    Detailed serializer for Query with logs
    """
    logs = QueryLogSerializer(many=True, read_only=True)

    class Meta(QuerySerializer.Meta):
        fields = QuerySerializer.Meta.fields + ['logs']


class TokenUsageLogSerializer(serializers.ModelSerializer):
    """
    Serializer for TokenUsageLog model
    """
    class Meta:
        model = TokenUsageLog
        fields = [
            'id', 'ai_agent_name', 'project', 'query', 'request_to_ai_agent',
            'ai_agent_answer', 'datetime', 'model_name', 'model_role',
            'prompt_tokens', 'completion_tokens', 'total_tokens',
            'precached_prompt_tokens', 'input_tokens', 'output_tokens',
            'system_prompt', 'user_prompt', 'agent_prompt'
        ]
        read_only_fields = ['id', 'datetime']


class TokenUsageStatsSerializer(serializers.Serializer):
    """
    Serializer for token usage statistics
    """
    total_tokens = serializers.IntegerField()
    total_requests = serializers.IntegerField()
    by_agent = serializers.DictField()
    by_model = serializers.DictField()