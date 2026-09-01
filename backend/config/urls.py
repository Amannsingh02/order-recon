from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.shortcuts import render
from django.http import HttpResponse
from django.views.static import serve
import os


def spa_view(request):
    """Serve the Vue SPA index.html for all non-API routes."""
    index_path = os.path.join(settings.BASE_DIR, 'static', 'frontend', 'index.html')
    if os.path.exists(index_path):
        with open(index_path, 'r', encoding='utf-8') as f:
            return HttpResponse(f.read(), content_type='text/html')
    return render(request, 'index.html')


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path(
        'assets/<path:path>',
        serve,
        {'document_root': os.path.join(settings.BASE_DIR, 'static', 'frontend', 'assets')},
    ),
    path('', spa_view, name='spa'),
]

# In production, WhiteNoise handles static files.
# This is only for local dev when not using WhiteNoise.
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
