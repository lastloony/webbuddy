from django.db import models


class Project(models.Model):
    """
    Модель для хранения параметров проекта (АС)
    """
    project_name = models.CharField(max_length=128, verbose_name='Project Name')
    test_it_token = models.CharField(max_length=128, blank=True, verbose_name='TestIt Token')
    test_it_project_id = models.CharField(max_length=128, blank=True, verbose_name='TestIt Project ID')
    jira_token = models.CharField(max_length=128, blank=True, verbose_name='Jira Token')
    jira_project_id = models.CharField(max_length=128, blank=True, verbose_name='Jira Project ID')
    project_context = models.TextField(blank=True, verbose_name='Project Context')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')

    class Meta:
        db_table = 'projects'
        verbose_name = 'Project'
        verbose_name_plural = 'Projects'

    def __str__(self):
        return self.project_name