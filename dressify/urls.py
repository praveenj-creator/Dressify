from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from app import views

# Context processor to inject nav_categories everywhere
from django.template.context_processors import request as req

urlpatterns = [
    path('', include('app.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
