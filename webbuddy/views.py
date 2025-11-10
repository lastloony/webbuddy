from django.views.generic import TemplateView
from django.conf import settings
import os


class ReactAppView(TemplateView):
    """
    Serve React application
    """
    template_name = 'index.html'

    def get_template_names(self):
        # In production, serve the React build
        if not settings.DEBUG:
            return [os.path.join(settings.BASE_DIR, 'frontend', 'dist', 'index.html')]
        # In development, you would run React dev server separately
        return [self.template_name]