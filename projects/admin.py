from django.contrib import admin
from .models import Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    """
    Admin interface for Project model
    """
    list_display = ('project_name', 'test_it_project_id', 'jira_project_id', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('project_name', 'test_it_project_id', 'jira_project_id')
    fieldsets = (
        ('Basic Information', {
            'fields': ('project_name', 'project_context')
        }),
        ('TestIt Integration', {
            'fields': ('test_it_token', 'test_it_project_id'),
            'classes': ('collapse',)
        }),
        ('Jira Integration', {
            'fields': ('jira_token', 'jira_project_id'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_at', 'updated_at')