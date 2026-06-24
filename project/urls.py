"""Rotas do projeto: apenas o painel de administração e ficheiros media."""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('escola/', include('escola.urls')),
    path('portfolio/', include('portfolio.urls')),
    path('', include('escola.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
