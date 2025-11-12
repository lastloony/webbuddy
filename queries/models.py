from django.db import models
from django.conf import settings


class Query(models.Model):
    """
    Модель для запросов/заявок пользователей
    """
    STATUS_CHOICES = [
        ('queued', 'Queued'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
        ('failed', 'Failed'),
    ]

    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='queries',
        verbose_name='Project'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='queries',
        verbose_name='User'
    )
    query_text = models.TextField(verbose_name='Query Text')
    answer_text = models.TextField(blank=True, verbose_name='Answer Text')
    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default='queued',
        verbose_name='Status'
    )
    query_created = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    query_finished = models.DateTimeField(null=True, blank=True, verbose_name='Finished At')

    class Meta:
        db_table = 'queries'
        verbose_name = 'Query'
        verbose_name_plural = 'Queries'
        ordering = ['-query_created']

    def __str__(self):
        return f"Query #{self.id} - {self.status}"


class QueryLog(models.Model):
    """
    Модель для логов выполнения запросов
    """
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='logs',
        verbose_name='Project'
    )
    query = models.ForeignKey(
        Query,
        on_delete=models.CASCADE,
        related_name='logs',
        verbose_name='Query'
    )
    log_data = models.TextField(verbose_name='Log Data')
    create_dtime = models.DateTimeField(auto_now_add=True, verbose_name='Created At')

    class Meta:
        db_table = 'query_logs'
        verbose_name = 'Query Log'
        verbose_name_plural = 'Query Logs'
        ordering = ['create_dtime']

    def __str__(self):
        return f"Log for Query #{self.query.id}"


class TokenUsageLog(models.Model):
    """
    Модель для отслеживания использования токенов AI-агентами и статистики
    """
    ai_agent_name = models.CharField(max_length=50, verbose_name='AI Agent Name')
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='token_logs',
        verbose_name='Project'
    )
    query = models.ForeignKey(
        Query,
        on_delete=models.CASCADE,
        related_name='token_logs',
        verbose_name='Query'
    )
    request_to_ai_agent = models.TextField(verbose_name='Request to AI Agent')
    ai_agent_answer = models.TextField(verbose_name='AI Agent Answer')
    datetime = models.DateTimeField(auto_now_add=True, verbose_name='Date Time')
    model_name = models.CharField(max_length=50, verbose_name='Model Name')
    model_role = models.CharField(max_length=50, verbose_name='Model Role')
    prompt_tokens = models.IntegerField(default=0, verbose_name='Prompt Tokens')
    completion_tokens = models.IntegerField(default=0, verbose_name='Completion Tokens')
    total_tokens = models.IntegerField(default=0, verbose_name='Total Tokens')
    precached_prompt_tokens = models.IntegerField(default=0, verbose_name='Precached Prompt Tokens')
    input_tokens = models.IntegerField(default=0, verbose_name='Input Tokens')
    output_tokens = models.IntegerField(default=0, verbose_name='Output Tokens')
    system_prompt = models.TextField(blank=True, verbose_name='System Prompt')
    user_prompt = models.TextField(blank=True, verbose_name='User Prompt')
    agent_prompt = models.TextField(blank=True, verbose_name='Agent Prompt')

    class Meta:
        db_table = 'token_usage_logs'
        verbose_name = 'Token Usage Log'
        verbose_name_plural = 'Token Usage Logs'
        ordering = ['-datetime']

    def __str__(self):
        return f"{self.ai_agent_name} - {self.total_tokens} tokens"