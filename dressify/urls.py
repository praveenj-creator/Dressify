from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from app import views
from app.health_check import health_check, detailed_health_check

# Context processor to inject nav_categories everywhere
from django.template.context_processors import request as req

urlpatterns = [
    # Health checks (useful for debugging)
    path('health/', health_check, name='health_check'),
    path('health/detailed/', detailed_health_check, name='detailed_health_check'),
    
    # Admin
    path('admin/', admin.site.urls),
    
    # App URLs
    path('', include('app.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

