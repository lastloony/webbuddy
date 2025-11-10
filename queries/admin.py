from django.contrib import admin
from .models import Query, QueryLog, TokenUsageLog


class QueryLogInline(admin.TabularInline):
    """
    Inline admin for QueryLog
    """
    model = QueryLog
    extra = 0
    readonly_fields = ('create_dtime',)
    can_delete = False


@admin.register(Query)
class QueryAdmin(admin.ModelAdmin):
    """
    Admin interface for Query model
    """
    list_display = ('id', 'project', 'user', 'status', 'query_created', 'query_finished')
    list_filter = ('status', 'project', 'query_created')
    search_fields = ('query_text', 'answer_text', 'user__username')
    readonly_fields = ('query_created', 'query_finished')
    inlines = [QueryLogInline]

    fieldsets = (
        ('Query Information', {
            'fields': ('project', 'user', 'query_text', 'status')
        }),
        ('Response', {
            'fields': ('answer_text',)
        }),
        ('Timestamps', {
            'fields': ('query_created', 'query_finished')
        }),
    )


@admin.register(QueryLog)
class QueryLogAdmin(admin.ModelAdmin):
    """
    Admin interface for QueryLog model
    """
    list_display = ('query', 'project', 'create_dtime', 'log_data_preview')
    list_filter = ('project', 'create_dtime')
    search_fields = ('log_data', 'query__id')
    readonly_fields = ('create_dtime',)

    def log_data_preview(self, obj):
        return obj.log_data[:100] + '...' if len(obj.log_data) > 100 else obj.log_data

    log_data_preview.short_description = 'Log Preview'


@admin.register(TokenUsageLog)
class TokenUsageLogAdmin(admin.ModelAdmin):
    """
    Admin interface for TokenUsageLog model
    """
    list_display = ('ai_agent_name', 'project', 'query', 'model_name', 'total_tokens', 'datetime')
    list_filter = ('ai_agent_name', 'model_name', 'project', 'datetime')
    search_fields = ('ai_agent_name', 'model_name', 'query__id')
    readonly_fields = ('datetime',)

    fieldsets = (
        ('Agent Information', {
            'fields': ('ai_agent_name', 'project', 'query', 'model_name', 'model_role')
        }),
        ('Request/Response', {
            'fields': ('request_to_ai_agent', 'ai_agent_answer')
        }),
        ('Token Usage', {
            'fields': ('prompt_tokens', 'completion_tokens', 'total_tokens',
                      'precached_prompt_tokens', 'input_tokens', 'output_tokens')
        }),
        ('Prompts', {
            'fields': ('system_prompt', 'user_prompt', 'agent_prompt'),
            'classes': ('collapse',)
        }),
        ('Timestamp', {
            'fields': ('datetime',)
        }),
    )